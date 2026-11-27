# Copyright (c) 2026 Klumzy Duk Gamez
# See LICENSE.md for terms.

import sys
import os

from typing import Any

import tomllib

import subprocess

import colorama

CONFIG_PATH: str = os.path.join(os.getcwd(), "config.toml")
BUILD_PATH: str = os.path.join(os.getcwd(), "build")
BUILD_OUTPUT_PATH: str = os.path.join(os.getcwd(), "build_out")

type config_t = dict[str, Any]
type command_t = list[str]


def print_command(cmd: command_t) -> None:
    for i in cmd:
        print(colorama.Fore.MAGENTA + f"{i} ", end="")
    print("")


def run_command(cmd: command_t, cwd: str) -> int:
    try:
        result = subprocess.run(
            cmd, shell=True, cwd=cwd, capture_output=True, text=True
        )
        print(colorama.Fore.CYAN + "[WGK] stdout for command: ", end="")
        print_command(cmd)
        print(result.stdout)
        print(colorama.Fore.CYAN + "[WGK] stderr for command: ", end="")
        print_command(cmd)
        print(colorama.Fore.YELLOW + result.stderr)
        return result.returncode
    except Exception:
        print(colorama.Fore.RED + "[WGK] Failed to run command: ", end="")
        print_command(cmd)
        return 1


def load_config(path: str) -> config_t:
    try:
        with open(path, "rb") as file:
            return tomllib.load(file)
    except FileNotFoundError:
        print(
            colorama.Fore.RED
            + f'[WGK] No config file exists at location "{CONFIG_PATH}"'
        )
        return {}
    except tomllib.TOMLDecodeError:
        print(
            colorama.Fore.RED
            + f'[WGK] Failed to parse config file at location "{CONFIG_PATH}"'
        )
        return {}
    except Exception:
        print(
            colorama.Fore.RED
            + f'[WGK] Failed to load config file at location "{CONFIG_PATH}"'
        )
        return {}


def verify_config(config: config_t) -> bool:
    keys: dict[str, list[str] | None] = {"project": ["name"], "build": ["generator"]}

    for k, j in keys.items():
        if k not in config:
            print(colorama.Fore.RED + f'[WGK] No "{k}" found in config')
            return False
        if j:
            for i in j:
                if i not in config[k]:
                    print(colorama.Fore.RED + f'[WGK] No "{k}.{i}" found in config')
                    return False

    return True


def construct_config_command(config: config_t) -> command_t:
    cmd: command_t = ["emcmake", "cmake", "..", "--fresh"]

    cmd.append(f"-G{config['build']['generator']}")

    cmd.append(f"-DCMAKE_INSTALL_PREFIX={BUILD_OUTPUT_PATH}")

    options: dict[str, str | tuple[str, str]] = {
        "WGK_CONFIG_PROJECT_NAME": ("project", "name")
    }

    for k, j in options.items():
        arg: str = f"-D{k}="
        if isinstance(j, str):
            arg += config[j]
        elif isinstance(j, tuple):
            arg += config[j[0]][j[1]]
        cmd.append(arg)

    return cmd


def construct_build_command(config: config_t) -> command_t:
    cmd: command_t = ["cmake", "--build", "."]
    return cmd


def construct_install_command(config: config_t) -> command_t:
    cmd: command_t = ["cmake", "--install", "."]
    return cmd


def main() -> int:
    colorama.init(autoreset=True)

    os.makedirs(BUILD_PATH, exist_ok=True)

    config: config_t = load_config(CONFIG_PATH)
    if not config:
        return 1

    if not verify_config(config):
        return 1

    result = run_command(construct_config_command(config), BUILD_PATH)
    if result:
        print(colorama.Fore.RED + "[WGK] Failed to configure cmake")
        return result

    result = run_command(construct_build_command(config), BUILD_PATH)
    if result:
        print(colorama.Fore.RED + "[WGK] Failed to build cmake")
        return result

    result = run_command(construct_install_command(config), BUILD_PATH)
    if result:
        print(colorama.Fore.RED + "[WGK] Failed to install cmake")
        return result

    return 0


if __name__ == "__main__":
    sys.exit(main())
