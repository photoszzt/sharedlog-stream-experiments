use std::fs::File;
use std::io::Read;
use std::io::Write;
use std::iter;
use std::path::Path;
use std::path::PathBuf;
use std::time;

use anyhow::anyhow;
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
    Scan {
        input: PathBuf,
        output: Option<PathBuf>,
        prefix: String,
    },
}

// Note: maximum latency should definitely be below 15 minutes
const MAX_LATENCY: u64 = 1_000 * 60 * 15;
const SIG_FIGURES: u8 = 3;

fn main() -> anyhow::Result<()> {
    let mut arguments = pico_args::Arguments::from_env();

    let command = match arguments.subcommand()?.as_deref() {
        Some("compress") => Command::Compress {
            output: arguments.opt_value_from_str("--output")?,
            inputs: iter::from_fn(|| arguments.opt_free_from_str().transpose())
                .collect::<Result<Vec<_>, _>>()?,
        },
        Some("scan") => Command::Scan {
            output: arguments.opt_value_from_str("--output")?,
            prefix: arguments.value_from_str("--prefix")?,
            input: arguments.free_from_str()?,
        },
        Some("query") => Command::Query {
            pretty: arguments.contains("--pretty"),
            input: arguments.opt_free_from_str()?,
        },
        None | Some(_) => return Err(anyhow!("Expected one of [compress, scan, query]")),
    };

    match command {
        Command::Compress { inputs, output } => {
            let mut histogram = Histogram::new_with_max(MAX_LATENCY, SIG_FIGURES)?;

            for input in inputs {
                latency::compress_file(input, &mut histogram)?;
            }

            let mut output = latency::writer(output.as_deref())
                .map(|file| flate2::write::GzEncoder::new(file, flate2::Compression::default()))?;

            V2Serializer::new().serialize(&histogram, &mut output)?;
        }

        Command::Scan {
            input,
            output,
            prefix,
        } => {
            for entry in input.read_dir()?.filter_map(Result::ok) {
                let name = entry.file_name();
                let name = name.to_string_lossy();
                let time = entry
                    .metadata()?
                    .created()?
                    .duration_since(time::UNIX_EPOCH)?
                    .as_secs();

                let delivery = if name.ends_with("alo") {
                    "alo"
                } else if name.ends_with("epoch") {
                    "eo"
                } else {
                    panic!("Expected `alo` or `epoch`, but got: {}", name);
                };

                let (tps, _) = name.split_once("tps_").expect("Expected `tps_` delimiter");

                let mut histogram = Histogram::new_with_max(MAX_LATENCY, SIG_FIGURES)?;

                let cache = match output.as_deref() {
                    None => None,
                    Some(path) => {
                        let file = File::options()
                            .create(true)
                            .write(true)
                            .open(path.join(format!("{}-{}-{}.hist.gz", delivery, tps, time)))?;

                        // Short-circuit with cached histogram
                        if file.metadata()?.len() > 0 {
                            let histogram = read_histogram(file)?;
                            report_histogram(&histogram, delivery, tps, false);
                            continue;
                        }

                        Some(file)
                    }
                };

                for entry in entry
                    .path()
                    .join("stats")
                    .read_dir()?
                    .filter_map(Result::ok)
                {
                    let name = entry.file_name();
                    let name = name.to_string_lossy();

                    if !name.starts_with(&prefix) {
                        continue;
                    }

                    latency::compress_file(entry.path(), &mut histogram)?;
                }

                report_histogram(&histogram, delivery, tps, false);

                if let Some(file) = cache {
                    write_histogram(file, &histogram)?;
                }
            }
        }

        Command::Query { input, pretty } => {
            let path = input.as_deref().unwrap_or_else(|| Path::new(""));
            let path = path.to_string_lossy();
            let (delivery, tps) = path
                .split_once('-')
                .and_then(|(delivery, next)| {
                    let (tps, _) = next.split_once('-')?;
                    Some((delivery, tps))
                })
                .unwrap_or(("?", "?"));

            let histogram = read_histogram(latency::reader(input.as_deref())?)?;
            report_histogram(&histogram, delivery, tps, pretty);
        }
    }

    Ok(())
}

fn read_histogram<R: Read>(reader: R) -> anyhow::Result<Histogram<u32>> {
    let mut reader = flate2::read::GzDecoder::new(reader);
    let histogram = Deserializer::new().deserialize(&mut reader)?;
    Ok(histogram)
}

fn write_histogram<W: Write>(writer: W, histogram: &Histogram<u32>) -> anyhow::Result<()> {
    let mut writer = flate2::write::GzEncoder::new(writer, flate2::Compression::default());
    V2Serializer::new().serialize(histogram, &mut writer)?;
    Ok(())
}

fn report_histogram(histogram: &Histogram<u32>, delivery: &str, tps: &str, pretty: bool) {
    if pretty {
        println!("del: {}", delivery);
        println!("tps: {}", tps);
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
            "{},{},{:.03},{:.03},{},{},{},{},{},{},{}",
            delivery,
            tps,
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
