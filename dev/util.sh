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
