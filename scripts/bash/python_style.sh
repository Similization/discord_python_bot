#! /bin/bash

dir=$PWD

scripts_dir="$(dirname "$dir")"
project_dir="$(dirname "$scripts_dir")"

black "$project_dir"
