# Extract important variables from the GitHub GraphQL JSON response
data = j["data"]

# Rate limit information
rate_limit = {
    "max_requests": data["rateLimit"]["limit"],  # Maximum allowed requests
    "remaining_requests": data["rateLimit"]["remaining"],  # Remaining requests in the current window
    "reset_time": data["rateLimit"]["resetAt"],  # Time when the rate limit resets
}

# Repository information
repository = data["repository"]

# Default branch commit history
default_branch_commit = {
    "total_commits": repository["defaultBranchRef"]["target"]["history"]["totalCount"],  # Total number of commits
    "latest_commit_oid": repository["defaultBranchRef"]["target"]["history"]["edges"][0]["node"]["oid"],  # Latest commit hash (OID)
    "latest_commit_date": repository["defaultBranchRef"]["target"]["history"]["edges"][0]["node"]["committedDate"],  # Latest commit date
}

# Tags information
tags = [
    edge["node"]["name"] for edge in repository["refs"]["edges"]
]  # List of tag names (if available)

# Releases information
releases = [
    {
        "name": release["node"]["name"],  # Release name
        "url": release["node"]["url"],  # Release URL
        "tag": release["node"]["tagName"],  # Tag associated with the release
        "is_prerelease": release["node"]["isPrerelease"],  # Whether this is a pre-release
        "is_latest": release["node"]["isLatest"],  # Whether this is the latest release
        "created_at": release["node"]["createdAt"],  # Release creation date
    }
    for release in repository["releases"]["edges"]
]

# Pagination info for releases
releases_pagination = {
    "has_next_page": repository["releases"]["pageInfo"]["hasNextPage"],  # Whether there are more releases
    "end_cursor": repository["releases"]["pageInfo"]["endCursor"],  # Cursor for the next page of releases
}

# Organized result as a dictionary
result = {
    "rate_limit": rate_limit,
    "default_branch_commit": default_branch_commit,
    "tags": tags,
    "releases": releases,
    "releases_pagination": releases_pagination,
}

# Example of accessing the organized data
print(result)