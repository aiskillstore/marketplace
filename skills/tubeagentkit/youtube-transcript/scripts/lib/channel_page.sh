# Sourced by the paged channel scripts (after lib/key.sh). One page of a channel list.
#
#   fetch_channel_page <videos|playlists|posts> <channel> <continuation> [name=value ...]
#
# A first page takes the channel plus any extra query parameters; a later page takes only the previous
# response's data.continuation_token (opaque, passed back verbatim). 1 credit per page either way.
fetch_channel_page() {
    local endpoint="$1" channel="$2" continuation="$3"
    shift 3

    local query=()
    if [ -n "$continuation" ]; then
        query+=(--data-urlencode "continuation=${continuation}")
    else
        query+=(--data-urlencode "channel=${channel}")
        local extra
        for extra in "$@"; do
            query+=(--data-urlencode "$extra")
        done
    fi

    curl -s -G "${API_BASE}/channel/${endpoint}" "${query[@]}" \
        -H "Authorization: Bearer ${YOUTUBE_TRANSCRIPT_API_KEY}"
}
