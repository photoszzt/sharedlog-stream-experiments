use std::fs;
use std::fs::File;
use std::iter;
use std::path::PathBuf;
use std::time;

use anyhow::anyhow;
use anyhow::Context as _;
use latency::histogram;
use walkdir::WalkDir;

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

    /// Plot distributions from gzipped HDR histograms.
    Plot {
        /// Include distributions with delivery semantics `delivery`.
        delivery: String,

        /// Include distributions with maximum latency below `max_latency`.
        max_latency: Option<u64>,

        /// Exclude throughputs in `exclude`.
        exclude: Vec<u32>,

        /// Include throughputs in `include`.
        include: Vec<u32>,

        /// Plot using a linear Y-axis instead of logarithmic.
        linear: bool,

        /// Load histograms from paths in `inputs`.
        inputs: Vec<PathBuf>,

        /// Output SVG file to `output`.
        output: PathBuf,
    },
}

fn main() -> anyhow::Result<()> {
    match Command::parse()? {
        Command::Compress { inputs, output } => {
            let mut histogram = histogram::new();

            for input in inputs {
                latency::compress_file(input, &mut histogram)?;
            }

            histogram::write(latency::writer(output.as_deref())?, &histogram)?;
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
                } else if name.ends_with("epoch") || name.ends_with("eo") {
                    "eo"
                } else {
                    panic!("Expected `alo` or `epoch`, but got: {}", name);
                };

                let (throughput, _) = name.split_once("tps_").expect("Expected `tps_` delimiter");

                let mut histogram = histogram::new();

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
                            let histogram = histogram::read(file)?;
                            histogram::report(&histogram, delivery, throughput, 1, false);
                            continue;
                        }

                        Some((path, file))
                    }
                };

                WalkDir::new(entry.path())
                    // Descend into `stats` (sys/boki) or `logs` (kafka) directory
                    .min_depth(2)
                    .into_iter()
                    .filter_map(Result::ok)
                    .filter(|entry| entry.file_type().is_file())
                    .filter(|entry| entry.file_name().to_string_lossy().starts_with(&prefix))
                    .try_for_each(|entry| latency::compress_file(entry.path(), &mut histogram))?;

                match histogram.is_empty() {
                    true => println!("{},{},x,x,x,x,x,x,x,x,x,x,x", delivery, throughput),
                    false => histogram::report(&histogram, delivery, throughput, 1, false),
                }

                match cache {
                    None => (),
                    Some((path, file)) if histogram.is_empty() => {
                        drop(file);
                        fs::remove_file(path)?;
                    }
                    Some((_, file)) => histogram::write(file, &histogram)?,
                }
            }
        }

        Command::Query { inputs, pretty } => histogram::read_all(&inputs)?.into_iter().for_each(
            |((delivery, throughput), (trials, histogram))| {
                histogram::report(&histogram, &delivery, &throughput, trials, pretty);
            },
        ),

        Command::Plot {
            inputs,
            output,
            delivery,
            max_latency,
            linear,
            include,
            exclude,
        } => {
            let data = histogram::read_all(&inputs)?
                .into_iter()
                .filter(|((delivery_, _), _)| delivery == *delivery_)
                .filter(|((_, throughput), _)| exclude.is_empty() || !exclude.contains(throughput))
                .filter(|((_, throughput), _)| include.is_empty() || include.contains(throughput))
                .filter(|(_, (_, histogram))| {
                    max_latency.map_or(true, |max_latency| histogram.max() <= max_latency)
                })
                .map(|((_, throughput), (_, histogram))| (throughput, histogram))
                .collect::<Vec<_>>();

            if data.is_empty() {
                return Err(anyhow!("No valid histograms found"));
            }

            latency::plot(output, &data, linear)?;
        }
    }

    Ok(())
}

impl Command {
    pub fn parse() -> anyhow::Result<Self> {
        let mut arguments = pico_args::Arguments::from_env();

        let command = match arguments.subcommand()?.as_deref() {
            Some("compress") => Command::Compress {
                output: match arguments.opt_value_from_str("-o")? {
                    Some(output) => Some(output),
                    None => arguments.opt_value_from_str("--output")?,
                },
                inputs: iter::from_fn(|| arguments.opt_free_from_str().transpose())
                    .collect::<Result<Vec<_>, _>>()?,
            },
            Some("scan") => Command::Scan {
                output: match arguments.opt_value_from_str("-o")? {
                    Some(output) => Some(output),
                    None => arguments.opt_value_from_str("--output")?,
                },
                prefix: arguments
                    .value_from_str("-p")
                    .or_else(|_| arguments.value_from_str("--prefix"))?,
                input: arguments.free_from_str()?,
            },
            Some("query") => Command::Query {
                pretty: arguments.contains(["-p", "--pretty"]),
                inputs: iter::from_fn(|| arguments.opt_free_from_str().transpose())
                    .collect::<Result<Vec<_>, _>>()
                    .map(|mut inputs| {
                        if inputs.is_empty() {
                            inputs.push(PathBuf::from("-"));
                        }
                        inputs
                    })?,
            },
            Some("plot") => Command::Plot {
                output: arguments
                    .value_from_str("-o")
                    .or_else(|_| arguments.value_from_str("--output"))?,
                max_latency: match arguments.opt_value_from_str("-m")? {
                    Some(max_latency) => Some(max_latency),
                    None => arguments.opt_value_from_str("--max-latency")?,
                },
                include: arguments
                    .values_from_str("--include")?
                    .into_iter()
                    .chain(arguments.values_from_str("-i")?)
                    .collect(),
                exclude: arguments
                    .values_from_str("--exclude")?
                    .into_iter()
                    .chain(arguments.values_from_str("-e")?)
                    .collect(),
                delivery: arguments
                    .value_from_str("-d")
                    .or_else(|_| arguments.value_from_str("--delivery"))?,
                linear: arguments.contains(["-l", "--linear"]),
                inputs: iter::from_fn(|| arguments.opt_free_from_str().transpose())
                    .collect::<Result<Vec<_>, _>>()
                    .map(|mut inputs| {
                        if inputs.is_empty() {
                            inputs.push(PathBuf::from("-"));
                        }
                        inputs
                    })?,
            },
            None | Some(_) => return Err(anyhow!("Expected one of [compress, scan, query, plot]")),
        };

        Ok(command)
    }
}
