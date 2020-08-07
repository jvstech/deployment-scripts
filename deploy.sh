#!/usr/bin/env bash

set -euET -o pipefail
shopt -s inherit_errexit

main()
{
  local deploymentRepo="https://api.github.com/repos/jvstech/deployment-scripts/tarball"
  local deploymentScript="deploy.py"
  
  local scriptDir="$(cd "$(dirname "${BASH_SOURCE[0]}")" >/dev/null 2>&1 && pwd)"
  local wd=$(pwd)
  local aptPath=$(find-apt)
  local pythonPath=$(which python3.8)
  local gitPath=$(which git)
  local curlPath=$(which curl)
  
  echo "Updating and upgrading ..."
  run-apt update
  run-apt upgrade
    
  echo "Checking for Python 3.8 ..."
  if [[ -z "$pythonPath" ]]; then
    echo "Python 3.8 not found; installing it now."
    run-apt install python3.8
  fi
  
  echo "Checking for git ..."
  if [[ -z "$gitPath" ]]; then
    echo "git not found; installing it now."
    run-apt install git
  fi
  
  echo "Checking for curl ..."
  if [[ -z "$curlPath" ]]; then
    echo "curl not found; installing it now."
    run-apt install curl
  fi
  
  echo "Checking for deployment scripts ..."
  if [[ ! -f "$scriptDir/$deploymentScript" ]]; then
    if [[ -d "$scriptDir/.git" ]]; then
      local remoteOrigin=$(git config --get remote.origin.url)
      if [[ "$remoteOrigin" == */deployment-scripts.git ]]; then
        throw "Not downloading scripts as this is a deployment " \
          "script repo checkout."
      fi
    fi
    
    echo "Downloading remaining deployment scripts ..."
    curl -L $deploymentRepo | tar zx --strip=1
    [[ -f "$scriptDir/$deploymentScript" ]] || \
      throw "Error: Deployment scripts still not found after download."
  fi
  
  $pythonPath $scriptDir/$deploymentScript
}

run-apt()
{
  local aptPath=$(find-apt)
  $aptPath $@ -y
}

find-apt()
{
  local aptPath=$(which apt)
  [[ -z "$aptPath" ]] && throw -e \
    "Couldn't find apt.\nCurrently, only Aptitude-based distros are supported."
  echo "$aptPath"
}

throw()
{
  exitCode=1
  if [ $1 -eq $1 2> /dev/null ]; then
    exitCode=$1
    shift
  fi
  
  >&2 echo $@
  exit $exitCode
}

if [[ $EUID -ne 0 ]]; then
  echo "Restarting as root ..."
  sudo bash $0 "$@"
  exit $?
fi

main
