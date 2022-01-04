function format_date {
    release_year=$(date '+%Y')
    release_month=$(date '+%B')
    release_day=$(date '+%d')

    first_digit="${release_day:0:1}"
    second_digit="${release_day:1:1}"

    if [ "$first_digit" -eq '1' ]; then
        suffix="th"
    elif [ "$second_digit" -eq '1' ]; then
        suffix="st"
    elif [ "$second_digit" -eq '2' ]; then
        suffix="nd"
    elif [ "$second_digit" -eq '3' ]; then
        suffix="rd"
    else
        suffix="th"
    fi

    if [ $first_digit -eq '0' ]; then
        release_day="${second_digit}"
    fi

    echo "${release_month} ${release_day}${suffix} ${release_year}"
}

function length {
    echo -n "$@" | awk '{print length}'
}

function dashes {
    printf -- '-%.s' $(eval "echo {1.."$(($1))"}")
}

function get_version {
    python -c 'print(__import__("stubalyzer").__version__)'
}

function confirm() {
    local prompt default reply

    if [[ ${2:-} = 'Y' ]]; then
        prompt='Y/n'
        default='Y'
    elif [[ ${2:-} = 'N' ]]; then
        prompt='y/N'
        default='N'
    else
        prompt='y/n'
        default=''
    fi

    while true; do

        # Ask the question (not using "read -p" as it uses stderr not stdout)
        echo -n "$1 [$prompt] "

        # Read the answer (use /dev/tty in case stdin is redirected from somewhere else)
        read -r reply </dev/tty

        # Default?
        if [[ -z $reply ]]; then
            reply=$default
        fi

        # Check if the reply is valid
        case "$reply" in
            Y*|y*) return 0 ;;
            N*|n*) return 1 ;;
        esac

    done
}
