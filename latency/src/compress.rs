use std::io;
use std::io::BufRead;

use anyhow::Context as _;
use hdrhistogram::Histogram;

/// Parse Sys/Boki raw latency output and compress it into an HDR histogram.
pub fn compress<R: BufRead>(mut input: R, output: &mut Histogram<u32>) -> anyhow::Result<()> {
    let mut buffer = Vec::new();

    input
        .read_until(b'[', &mut buffer)
        .context("Expected opening '['")?;
    buffer.clear();

    let mut r#continue = true;

    while r#continue {
        match input.read_until(b',', &mut buffer) {
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
            .context("Expected valid UTF-8")?
            .parse::<u32>()
            .context("Expected unsigned integer")?;

        buffer.clear();
        output.record(time as u64)?;
    }

    Ok(())
}
