import argparse
from .io import load_config


def main():
    parser = argparse.ArgumentParser(description="Retail association rule temporal stability")
    parser.add_argument("command", choices=["download", "prepare", "pilot", "experiment", "supplement", "figures", "verify", "export-report", "all"])
    parser.add_argument("--config", default="configs/experiment.json")
    parser.add_argument("--report-dir", default=None)
    args = parser.parse_args()
    cfg = load_config(args.config)
    if args.command == "download":
        from .data import download
        download(cfg)
    if args.command in ["prepare", "all"]:
        from .data import prepare
        prepare(cfg)
    if args.command == "pilot":
        from .experiment import pilot
        pilot(cfg)
    if args.command in ["experiment", "all"]:
        from .experiment import run_experiments
        run_experiments(cfg)
    if args.command in ["supplement", "all"]:
        from .supplement import run_supplements
        run_supplements(cfg)
    if args.command in ["figures", "all"]:
        from .figures import build_figures
        build_figures(cfg)
    if args.command in ["verify", "all"]:
        from .verify import verify_results
        verify_results(cfg)
    if args.command == "export-report":
        from .export_report import export_report
        export_report(cfg, args.report_dir)
