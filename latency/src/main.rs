use std::collections::BTreeMap;
use std::fs::File;
use std::io;
use std::io::Read;
use std::io::Write;
use std::iter;
use std::path::PathBuf;
use std::time;

use anyhow::anyhow;
use anyhow::Context as _;
use hdrhistogram::serialization::Deserializer;
use hdrhistogram::serialization::Serializer as _;
use hdrhistogram::serialization::V2Serializer;
use hdrhistogram::Histogram;

fn main() -> anyhow::Result<()> {
    match Command::parse()? {
        Command::Compress { inputs, output } => {
            let mut histogram = new_histogram();

            for input in inputs {
                latency::compress_file(input, &mut histogram)?;
            }

            write_histogram(latency::writer(output.as_deref())?, &histogram)?;
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
                    .modified()?
                    .duration_since(time::UNIX_EPOCH)?
                    .as_secs();

                let delivery = if name.ends_with("alo") {
                    "alo"
                } else if name.ends_with("epoch") {
                    "eo"
                } else {
                    panic!("Expected `alo` or `epoch`, but got: {}", name);
                };

                let (throughput, _) = name.split_once("tps_").expect("Expected `tps_` delimiter");

                let mut histogram = new_histogram();

                let cache = match output.as_deref() {
                    None => None,
                    Some(path) => {
                        let path =
                            path.join(format!("{}-{}-{}.hist.gz", delivery, throughput, time));
                        let file = File::options()
                            .read(true)
                            .create(true)
                            .write(true)
                            .open(&path)
                            .with_context(|| anyhow!("Failed to open file: {}", path.display()))?;

                        // Short-circuit with cached histogram
                        if file.metadata()?.len() > 0 {
                            let histogram = read_histogram(file)?;
                            report_histogram(&histogram, delivery, throughput, 1, false);
                            continue;
                        }

                        Some(file)
                    }
                };

                let stats = entry.path().join("stats");

                match stats.read_dir() {
                    Ok(stats) => {
                        stats
                            .filter_map(Result::ok)
                            .filter(|entry| {
                                let name = entry.file_name();
                                let name = name.to_string_lossy();
                                name.starts_with(&prefix)
                            })
                            .try_for_each(|entry| {
                                latency::compress_file(entry.path(), &mut histogram)
                            })?;
                    }
                    Err(error) if error.kind() == io::ErrorKind::NotFound => (),
                    Err(error) => {
                        return Err(error).with_context(|| {
                            anyhow!("Failed to read directory: {}", stats.display())
                        })
                    }
                };

                if histogram.is_empty() {
                    println!("{},{},x,x,x,x,x,x,x,x,x,x,x", delivery, throughput);
                    continue;
                }

                report_histogram(&histogram, delivery, throughput, 1, false);

                if let Some(file) = cache {
                    write_histogram(file, &histogram)?;
                }
            }
        }

        Command::Query { inputs, pretty } => {
            let mut histograms = BTreeMap::default();

            for input in inputs {
                let partial = read_histogram(latency::reader(Some(&input))?)?;

                let (delivery, throughput) =
                    match input
                        .to_string_lossy()
                        .split_once('-')
                        .and_then(|(delivery, next)| {
                            let (throughput, _) = next.split_once('-')?;
                            Some((delivery.to_owned(), throughput.to_owned()))
                        }) {
                        Some((delivery, throughput)) => (delivery, throughput),
                        None => {
                            eprintln!("Ignoring unrecognized file: {}", input.display());
                            continue;
                        }
                    };

                let (trials, total) = histograms
                    .entry((delivery, throughput))
                    .or_insert_with(|| (0, new_histogram()));

                *trials += 1;
                *total += partial;
            }

            histograms
                .into_iter()
                .for_each(|((delivery, throughput), (trials, histogram))| {
                    report_histogram(&histogram, &delivery, &throughput, trials, pretty);
                })
        }
    }

    Ok(())
}

enum Command {
    /// Compress raw gzipped logs into gzipped HDR histograms.
    Compress {
        inputs: Vec<PathBuf>,
        output: Option<PathBuf>,
    },

    /// Print aggregate statistics from a gzipped HDR histogram.
    Query { inputs: Vec<PathBuf>, pretty: bool },

    /// Compress and report all aggregate statistics from experiment directory `input`.
    ///
    /// Only collects statistics from log files beginning with `prefix`.
    /// Optionally cache histograms under directory `output`.
    Scan {
        input: PathBuf,
        output: Option<PathBuf>,
        prefix: String,
    },
}

impl Command {
    pub fn parse() -> anyhow::Result<Self> {
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
                inputs: iter::from_fn(|| arguments.opt_free_from_str().transpose())
                    .collect::<Result<Vec<_>, _>>()
                    .map(|mut inputs| {
                        if inputs.is_empty() {
                            inputs.push(PathBuf::from("-"));
                        }
                        inputs
                    })?,
            },
            None | Some(_) => return Err(anyhow!("Expected one of [compress, scan, query]")),
        };

        Ok(command)
    }
}

fn new_histogram() -> Histogram<u32> {
    // Note: maximum latency should definitely be below 15 minutes
    Histogram::new_with_max(1_000 * 60 * 15, 3).expect("Expected valid histogram configuration")
}

fn read_histogram<R: Read>(reader: R) -> anyhow::Result<Histogram<u32>> {
    let mut reader = flate2::read::GzDecoder::new(reader);
    let histogram = Deserializer::new()
        .deserialize(&mut reader)
        .context("Failed to deserialize histogram")?;
    Ok(histogram)
}

fn write_histogram<W: Write>(writer: W, histogram: &Histogram<u32>) -> anyhow::Result<()> {
    let mut writer = flate2::write::GzEncoder::new(writer, flate2::Compression::default());
    V2Serializer::new()
        .serialize(histogram, &mut writer)
        .context("Failed to serialize histogram")?;
    Ok(())
}

fn report_histogram(
    histogram: &Histogram<u32>,
    delivery: &str,
    throughput: &str,
    trials: usize,
    pretty: bool,
) {
    if pretty {
        println!("delivery: {}", delivery);
        println!("throughput/sec/worker: {}", throughput);
        println!("\ttrials: {}", trials);
        println!("\tpoints: {}", histogram.len());
        println!("\tavg (ms): {:.03}", histogram.mean());
        println!("\tstd (ms): {:.03}", histogram.stdev());
        println!("\tmin (ms): {}", histogram.min());
        println!("\tp25 (ms): {}", histogram.value_at_quantile(0.25));
        println!("\tp50 (ms): {}", histogram.value_at_quantile(0.50));
        println!("\tp75 (ms): {}", histogram.value_at_quantile(0.75));
        println!("\tp90 (ms): {}", histogram.value_at_quantile(0.90));
        println!("\tp99 (ms): {}", histogram.value_at_quantile(0.99));
        println!("\tmax (ms): {}", histogram.max());
        println!();
    } else {
        println!(
            "{},{},{},{},{:.03},{:.03},{},{},{},{},{},{},{}",
            delivery,
            throughput,
            trials,
            histogram.len(),
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
