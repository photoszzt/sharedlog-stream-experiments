use std::fs;
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
        output: PathBuf,
    },
    Query(PathBuf),
}

fn main() -> anyhow::Result<()> {
    let mut arguments = pico_args::Arguments::from_env();

    let command = match arguments.subcommand()?.as_deref() {
        Some("compress") => Command::Compress {
            output: arguments.value_from_str("--output")?,
            inputs: iter::from_fn(|| arguments.opt_free_from_str().transpose())
                .collect::<Result<Vec<_>, _>>()?,
        },
        Some("query") => Command::Query(arguments.free_from_str()?),
        None | Some(_) => return Err(anyhow!("Expected one of [compress, decompress]")),
    };

    match command {
        Command::Compress { inputs, output } => {
            let mut output = fs::File::options()
                .write(true)
                .create_new(true)
                .open(output)
                .map(|file| flate2::write::GzEncoder::new(file, flate2::Compression::default()))?;

            for input in inputs {
                fs::File::open(&input)
                    .map(flate2::read::GzDecoder::new)
                    // Shouldn't need to parse entire JSON object here
                    .map(serde_json::from_reader::<_, serde_json::Value>)
                    .with_context(|| anyhow!("Could not open input file: `{}`", input.display()))??
                    .get_mut("Latencies")
                    .expect("Expected 'Latencies' key in metrics JSON")
                    .get_mut("eventTimeLatency_sink")
                    .expect("Expected 'eventTimeLatency_sink' key in metrics JSON")
                    .as_array_mut()
                    .map(|array| array.drain(..))
                    .expect("Expected .Latencies.eventTimeLatency_sink to be an array")
                    .map(|time| time.as_u64().expect("Expected latencies to be integers"))
                    .map(|time| {
                        u32::try_from(time).expect("Expected latencies to be below u32::MAX")
                    })
                    .try_for_each(|time| output.write_all(time.to_le_bytes().as_slice()))?;
            }
        }

        Command::Query(input) => {
            let mut histogram = Histogram::<u32>::new_with_max(u32::MAX as u64, 3)?;
            let mut input = fs::File::open(&input).map(flate2::read::GzDecoder::new)?;
            let mut buffer = [0u8; 1024];
            let mut total = 0;

            loop {
                match input.read(&mut buffer)? {
                    0 => break,
                    length => {
                        total += length;
                        buffer
                            .chunks(4)
                            .take(length >> 2)
                            .map(|chunk| u32::from_le_bytes(chunk.try_into().unwrap()))
                            .try_for_each(|time| histogram.record(time as u64))?;
                    }
                }
            }

            assert_eq!(total % 4, 0);
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
