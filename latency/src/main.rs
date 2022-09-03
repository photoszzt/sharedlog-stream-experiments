use std::fs::File;
use std::io;
use std::iter;
use std::path::PathBuf;

use anyhow::anyhow;
use anyhow::Context;
use hdrhistogram::serialization::Deserializer;
use hdrhistogram::serialization::Serializer as _;
use hdrhistogram::serialization::V2Serializer;
use hdrhistogram::Histogram;

enum Command {
    Compress {
        inputs: Vec<PathBuf>,
        output: Option<PathBuf>,
    },
    Query {
        input: Option<PathBuf>,
        pretty: bool,
    },
}

fn main() -> anyhow::Result<()> {
    let mut arguments = pico_args::Arguments::from_env();

    let command = match arguments.subcommand()?.as_deref() {
        Some("compress") => Command::Compress {
            output: arguments.opt_value_from_str("--output")?,
            inputs: iter::from_fn(|| arguments.opt_free_from_str().transpose())
                .collect::<Result<Vec<_>, _>>()?,
        },
        Some("query") => Command::Query {
            pretty: arguments.contains("--pretty"),
            input: arguments.opt_free_from_str()?,
        },
        None | Some(_) => return Err(anyhow!("Expected one of [compress, decompress]")),
    };

    match command {
        Command::Compress { inputs, output } => {
            let mut histogram = Histogram::new_with_max(u32::MAX as u64, 3)?;

            for input in inputs {
                let mut reader = File::open(&input)
                    .map(flate2::read::GzDecoder::new)
                    .map(io::BufReader::new)?;

                latency::compress(&mut reader, &mut histogram)?;
            }

            let mut output = latency::writer(output.as_deref())
                .map(|file| flate2::write::GzEncoder::new(file, flate2::Compression::default()))?;

            V2Serializer::new().serialize(&histogram, &mut output)?;
        }

        Command::Query { input, pretty } => {
            let mut input = latency::reader(input.as_deref())
                .map(flate2::read::GzDecoder::new)
                .with_context(|| anyhow!("Could not open input file: {:?}", input))?;

            let histogram = Deserializer::new().deserialize::<u32, _>(&mut input)?;

            if pretty {
                println!("avg: {:.03}ms", histogram.mean());
                println!("std: {:.03}ms", histogram.stdev());
                println!("min: {}ms", histogram.min());
                println!("p25: {}ms", histogram.value_at_quantile(0.25));
                println!("p50: {}ms", histogram.value_at_quantile(0.50));
                println!("p75: {}ms", histogram.value_at_quantile(0.75));
                println!("p90: {}ms", histogram.value_at_quantile(0.90));
                println!("p99: {}ms", histogram.value_at_quantile(0.99));
                println!("max: {}ms", histogram.max());
            } else {
                println!(
                    "{:.03},{:.03},{},{},{},{},{},{},{}",
                    histogram.mean(),
                    histogram.stdev(),
                    histogram.min(),
                    histogram.value_at_quantile(0.25),
                    histogram.value_at_quantile(0.50),
                    histogram.value_at_quantile(0.75),
                    histogram.value_at_quantile(0.90),
                    histogram.value_at_quantile(0.99),
                    histogram.max(),
                );
            }
        }
    }

    Ok(())
}
