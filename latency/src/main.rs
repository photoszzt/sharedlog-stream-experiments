use std::fs::File;
use std::io;
use std::io::BufRead;
use std::io::Read;
use std::io::Write;
use std::iter;
use std::path::PathBuf;

use anyhow::anyhow;
use anyhow::Context;
use hdrhistogram::Histogram;

enum Command {
    Compress {
        inputs: Vec<PathBuf>,
        output: Option<String>,
    },
    Query(PathBuf),
}

enum Or<L, R> {
    L(L),
    R(R),
}

impl<L: Write, R: Write> Write for Or<L, R> {
    fn write(&mut self, buffer: &[u8]) -> io::Result<usize> {
        match self {
            Or::L(left) => left.write(buffer),
            Or::R(right) => right.write(buffer),
        }
    }

    fn flush(&mut self) -> io::Result<()> {
        match self {
            Or::L(left) => left.flush(),
            Or::R(right) => right.flush(),
        }
    }
}

fn main() -> anyhow::Result<()> {
    let mut arguments = pico_args::Arguments::from_env();

    let command = match arguments.subcommand()?.as_deref() {
        Some("compress") => Command::Compress {
            output: arguments.opt_value_from_str("--output")?,
            inputs: iter::from_fn(|| arguments.opt_free_from_str().transpose())
                .collect::<Result<Vec<_>, _>>()?,
        },
        Some("query") => Command::Query(arguments.free_from_str()?),
        None | Some(_) => return Err(anyhow!("Expected one of [compress, decompress]")),
    };

    match command {
        Command::Compress { inputs, output } => {
            let mut output = match output.as_deref() {
                None | Some("-") => Ok(Or::L(io::stdout().lock())),
                Some(path) => File::options()
                    .write(true)
                    .create_new(true)
                    .open(path)
                    .map(Or::R),
            }
            .map(|file| flate2::write::GzEncoder::new(file, flate2::Compression::default()))?;

            let mut buffer = Vec::new();

            for input in inputs {
                let mut reader = File::open(&input)
                    .map(flate2::read::GzDecoder::new)
                    .map(io::BufReader::new)?;

                reader.read_until(b'[', &mut buffer).expect("Expected '['");
                buffer.clear();

                let mut r#continue = true;

                while r#continue {
                    match reader.read_until(b',', &mut buffer) {
                        Ok(_) => (),
                        Err(error) if error.kind() == io::ErrorKind::UnexpectedEof => (),
                        Err(error) => return Err(anyhow::Error::from(error)),
                    };

                    // Remove trailing delimiter (,)
                    buffer.pop();

                    // Remove non-numeric characters
                    loop {
                        match buffer.last() {
                            None | Some(b'0'..=b'9') => break,
                            Some(_) => {
                                r#continue = false;
                                buffer.pop();
                            }
                        }
                    }

                    let time = std::str::from_utf8(&buffer)
                        .expect("Expected valid UTF-8")
                        .parse::<u32>()
                        .expect("Expected unsigned integer")
                        .to_le_bytes();

                    buffer.clear();
                    output.write_all(&time)?;
                }
            }
        }

        Command::Query(input) => {
            let mut histogram = Histogram::<u32>::new_with_max(u32::MAX as u64, 3)?;
            let mut input = File::open(&input)
                .map(flate2::read::GzDecoder::new)
                .with_context(|| anyhow!("Could not open input file: {}", input.display()))?;

            let mut buffer = [0u8; 4];
            loop {
                match input.read_exact(&mut buffer) {
                    Ok(()) => histogram.record(u32::from_le_bytes(buffer) as u64)?,
                    Err(error) if error.kind() == io::ErrorKind::UnexpectedEof => break,
                    Err(error) => return Err(anyhow::Error::from(error)),
                }
            }

            println!("mean:  {:.03}ms", histogram.mean());
            println!("stdev: {:.03}ms", histogram.stdev());
            println!("min:   {}ms", histogram.min());
            println!("p25:   {}ms", histogram.value_at_quantile(0.25));
            println!("p50:   {}ms", histogram.value_at_quantile(0.50));
            println!("p75:   {}ms", histogram.value_at_quantile(0.75));
            println!("p90:   {}ms", histogram.value_at_quantile(0.90));
            println!("p99:   {}ms", histogram.value_at_quantile(0.99));
            println!("max:   {}ms", histogram.max());
        }
    }

    Ok(())
}
