#!/bin/bash

exec 3>&1
exec >&2

dir=$1
vcs=$2
get_tags=$3

parse_vcs_url() {
    local _url=$1
    local _out_var=$2
    # remove folder::
    [[ $_url =~ ^[^/:]*::(.*)$ ]] && _url=${BASH_REMATCH[1]}
    [[ $_url =~ ^(bzr|git|hg|svn)([+:])(.*) ]] || return 1
    local _proto=${BASH_REMATCH[1]}
    [[ ${BASH_REMATCH[2]} = + ]] && _url=${BASH_REMATCH[3]}
    local _real_url=${_url%\#*}
    local _frag=''
    [[ $_real_url = $_url ]] || _frag=${_url##*\#}
    eval "${_out_var}"'=("${_proto}" "${_real_url}" "${_frag}")'
}

get_vcs() {
    local _vcs=$1
    local _out_var=$2
    if [[ -z $_vcs ]]; then
        _vcs=$(. "${dir}"/PKGBUILD &> /dev/null
               for src in "${source[@]}"; do
                   parse_vcs_url "$src" _ && {
                       echo "$src"
                       exit 0
                   }
               done
               exit 1) || return 1
    fi
    parse_vcs_url "$_vcs" "$_out_var"
}

git_get_version() {
    local _url=$1
    local _frag=$2
    local _ref=''
    if [[ -z $_frag ]]; then
        _ref=HEAD
    elif [[ $_frag =~ ^commit=(.*)$ ]]; then
        echo "${BASH_REMATCH[1]}"
        return 0
    elif [[ $_frag =~ ^branch=(.*)$ ]]; then
        _ref=refs/heads/${BASH_REMATCH[1]}
    elif [[ $_frag =~ ^tag=(.*)$ ]]; then
        _ref=refs/tags/${BASH_REMATCH[1]}
    else
        return 1
    fi
    local _res=$(git ls-remote "$_url" "$_ref")
    [[ $_res =~ ^([a-fA-F0-9]*)[[:blank:]] ]] || return 1
    echo "${BASH_REMATCH[1]}"
}

hg_get_version() {
    local _url=$1
    local _frag=$2
    local _ref
    if [[ -z $_frag ]]; then
        _ref=default
    elif [[ $_frag =~ ^(revision|tag|branch)=(.*)$ ]]; then
        _ref=${BASH_REMATCH[2]}
    else
        return 1
    fi
    hg identify "${_url}#${_ref}"
}

svn_get_version() {
    local _url=$1
    local _frag=$2
    local _extra_arg=()
    if [[ -z $_frag ]]; then
        true
    elif [[ $_frag =~ ^(revision)=(.*)$ ]]; then
        _extra_arg=(-r "${BASH_REMATCH[2]}")
    else
        return 1
    fi
    # Get rid of locale
    env -i PATH="${PATH}" svn info "${_extra_arg[@]}" "${_url}" | \
        sed -n 's/^Revision:[[:blank:]]*\([0-9]*\)/\1/p'
}

bzr_get_version() {
    local _url=$1
    local _frag=$2
    local _extra_arg=()
    if [[ -z $_frag ]]; then
        true
    elif [[ $_frag =~ ^(revision)=(.*)$ ]]; then
        _extra_arg=(-r "${BASH_REMATCH[2]}")
    else
        return 1
    fi
    bzr revno -q "${_extra_arg[@]}" "${_url}"
}

git_get_tags() {
    local _url=$1
    git ls-remote "$_url" | grep -oP '(?<=refs/tags/)[^^]*$'
}

get_vcs "${vcs}" components || exit 1
if [[ "x$get_tags" == "xget_tags" ]]; then
  eval "${components[0]}_get_tags"' ${components[@]:1}' >&3
else
  eval "${components[0]}_get_version"' ${components[@]:1}' >&3
fi
