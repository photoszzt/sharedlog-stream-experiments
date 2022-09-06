use std::fs::File;
use std::io;
use std::io::BufRead;
use std::path::Path;

use anyhow::anyhow;
use anyhow::Context as _;
use hdrhistogram::Histogram;

pub fn compress_file<P: AsRef<Path>>(input: P, output: &mut Histogram<u32>) -> anyhow::Result<()> {
    File::open(&input)
        .map(|file| {
            if input
                .as_ref()
                .extension()
                .map_or(false, |extension| extension == "gz")
            {
                crate::Or::L(flate2::read::GzDecoder::new(file))
            } else {
                crate::Or::R(file)
            }
        })
        .map(io::BufReader::new)
        .map(|reader| compress_reader(reader, output))?
}

/// Parse Sys/Boki raw latency output and compress it into an HDR histogram.
fn compress_reader<R: BufRead>(mut input: R, output: &mut Histogram<u32>) -> anyhow::Result<()> {
    let mut buffer = String::new();

    loop {
        buffer.clear();

        match input.read_line(&mut buffer) {
            Ok(0) => break,
            Ok(_) => (),
            Err(error) if error.kind() == io::ErrorKind::UnexpectedEof => break,
            Err(error) => return Err(anyhow::Error::from(error)),
        }

        for line in buffer.trim().split('\n') {
            let lo = line
                .find('[')
                .ok_or_else(|| anyhow!("Expected opening '['"))?;

            let hi = line
                .find(']')
                .ok_or_else(|| anyhow!("Expected closing ']'"))?;

            line[lo + 1..hi]
                .split(',')
                .map(str::trim)
                .map(|time| time.parse::<u32>().context("Expected unsigned integer"))
                .try_for_each(|time| output.record(time? as u64).map_err(anyhow::Error::from))?;
        }
    }

    Ok(())
}
