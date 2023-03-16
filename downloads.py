import csv
import os
import urllib.request

import matplotlib.pyplot as plt
import github

downloads_by_version = {}


def download_spacedock(url, filename):
    script_dir = os.path.dirname(os.path.abspath(__file__))  # get the script directory
    resources_dir = os.path.join(script_dir, 'resources')  # construct the path to the resources directory
    if not os.path.exists(resources_dir):
        os.makedirs(resources_dir)
    file_path = os.path.join(script_dir, filename)  # construct the path to the output file
    with urllib.request.urlopen(url) as response, open(file_path, 'wb') as out_file:
        data = response.read()  # read the data from the response
        out_file.write(data)  # write the data to a local file


def download_github_releases(access_token, owner, repo, output_file):
    gh = github.Github(access_token)

    # get the repo
    repo = gh.get_repo(full_name_or_id=f"{owner}/{repo}")

    script_dir = os.path.dirname(os.path.abspath(__file__))
    output_file = os.path.join(script_dir, output_file)
    with open(output_file, mode='w', newline='') as csv_file:
        writer = csv.writer(csv_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        writer.writerow(['Date', 'Downloads', 'Mod Version'])

        for release in repo.get_releases():
            if not release.prerelease and release.tag_name.startswith('spacewarp-'):
                release_date = release.published_at.strftime('%Y-%m-%d %H:%M:%S.%f')
                mod_version = release.tag_name.replace('v', '').replace('spacewarp-', '').split('-')[0]
                download_count = sum([asset.download_count for asset in release.get_assets()])
                writer.writerow([release_date, download_count, mod_version])


def find_total_downloads(csv_files):
    script_dir = os.path.dirname(os.path.abspath(__file__))
    # Loop through each CSV file
    for file_name in csv_files:
        file_name = os.path.join(script_dir, file_name)
        with open(file_name, "r") as file:
            # Read in the CSV file as a dictionary
            reader = csv.DictReader(file)

            # Loop through each row in the CSV file
            for row in reader:
                # Extract the version and downloads from the row
                version = row["Mod Version"]
                downloads = int(row["Downloads"])

                # If the version is not in the dictionary yet, add it
                if version not in downloads_by_version:
                    downloads_by_version[version] = 0

                # Add the downloads to the total for the version
                downloads_by_version[version] += downloads

    # Sort the dictionary by version number
    sorted_by_version = dict(sorted(downloads_by_version.items(), key=lambda x: tuple(int(v) for v in x[0].split('.'))))

    return sorted_by_version


def print_total_downloads():
    # Sort the version numbers in ascending order
    versions_sorted = sorted(downloads_by_version.keys(), key=lambda v: tuple(map(int, v.split('.'))))

    # Print out the total downloads by version, sorted by version major.minor.patch
    for version in versions_sorted:
        downloads = downloads_by_version[version]
        print(f"Version {version}: {downloads} downloads")

    # Print out the total downloads for all versions
    total_downloads = sum(downloads_by_version.values())
    print(f"Total: {total_downloads:,} downloads")


def create_bar_chart():
    # Set the style to dark mode
    plt.style.use('dark_background')

    # Get the version numbers and download counts as separate lists
    versions = list(downloads_by_version.keys())
    download_counts = list(downloads_by_version.values())

    # Sort the version numbers in ascending order
    versions_sorted = sorted(versions, key=lambda v: tuple(map(int, v.split('.'))))

    # Sort the download counts to match the sorted version numbers
    download_counts_sorted = [downloads_by_version[v] for v in versions_sorted]

    # Set the colors and font styles for the bars and text
    bar_color = '#1f77b4'  # blue
    text_color = '#FFFFFF'  # white
    font_size = 14

    # Calculate the total number of downloads
    total_downloads = sum(download_counts)

    # Create a bar chart using Matplotlib
    plt.bar(versions_sorted, download_counts_sorted, color=bar_color)
    plt.xlabel('Version', color=text_color, fontsize=font_size)
    plt.ylabel('Downloads', color=text_color, fontsize=font_size)
    plt.title(f'Total Downloads by Version\n{total_downloads:,} total downloads', color=text_color, fontsize=font_size)
    plt.xticks(color=text_color, fontsize=10)
    plt.yticks(color=text_color, fontsize=12)
    plt.tight_layout()  # to prevent labels from getting clipped

    # Save the pie chart to a file in the out directory
    out_dir = os.path.join(os.path.dirname(__file__), 'out')
    if not os.path.exists(out_dir):
        os.makedirs(out_dir)
    plt.savefig(os.path.join(out_dir, 'bar_chart.png'), bbox_inches='tight')

    plt.subplots_adjust(left=0.15, right=0.95, top=0.85, bottom=0.15)

    plt.show()


def create_pie_chart():
    # Set the style to dark mode
    plt.style.use('dark_background')

    # Get the version numbers and download counts as separate lists
    versions = list(downloads_by_version.keys())
    download_counts = list(downloads_by_version.values())

    # Filter out versions with insignificant download counts
    threshold = 1000
    significant_versions = [v for v, c in downloads_by_version.items() if c >= threshold]
    significant_counts = [c for v, c in downloads_by_version.items() if c >= threshold]
    insignificant_count = sum([c for v, c in downloads_by_version.items() if c < threshold])
    total_count = sum(download_counts)

    # Sort the significant version numbers in ascending order
    significant_sorted = sorted(significant_versions, key=lambda v: tuple(map(int, v.split('.'))))

    # Sort the significant download counts to match the sorted version numbers
    significant_counts_sorted = [downloads_by_version[v] for v in significant_sorted]

    # Set the colors and font styles for the pie chart and text
    pie_colors = ['#ff7f0e', '#2ca02c', '#d62728', '#9467bd', '#1f77b4', '#989fa3', '#e377c2', '#7f7f7f', '#bcbd22', '#17becf']
    text_color = '#FFFFFF'  # white
    font_size = 12

    # Create a pie chart using Matplotlib
    fig, ax = plt.subplots()
    wedges, texts, autotexts = ax.pie(
        significant_counts_sorted + [insignificant_count],
        colors=pie_colors + ['#808080'],
        labels=significant_sorted + ['Others'],
        autopct=lambda pct: f"{pct:.1f}%" if pct > 5 else '',
        textprops=dict(color=text_color, fontsize=font_size),
        wedgeprops=dict(width=0.5),
        pctdistance=0.8,
        startangle=90
    )
    # Set the font size for the percentages
    for autotext in autotexts:
        autotext.set_fontsize(font_size)

    # Set the title for the pie chart
    title_text = f"Total Downloads by Version"  # Add the total count to the title
    ax.set_title(title_text, color=text_color, fontsize=font_size, loc='center', pad=20)

    # Set text to the center of the pie chart
    ax.text(0, 0, f"{total_count:,}\nDownloads", color=text_color, fontsize=font_size, ha='center', va='center')

    # Set the aspect ratio to be equal so that the pie chart is circular
    ax.axis('equal')

    # Save the pie chart to a file in the out directory
    out_dir = os.path.join(os.path.dirname(__file__), 'out')
    if not os.path.exists(out_dir):
        os.makedirs(out_dir)
    plt.savefig(os.path.join(out_dir, 'pie_chart.png'), bbox_inches='tight')

    fig.subplots_adjust(left=0.15, right=0.85, top=0.85, bottom=0.15)

    # Display the pie chart
    plt.show()


def main(access_token):
    download_spacedock(
        "https://spacedock.info/mod/3257/Space%20Warp/stats/downloads",
        "resources/spacedock_spacewarp.csv"
    )
    download_spacedock(
        "https://spacedock.info/mod/3277/Space%20Warp%20+%20BepInEx/stats/downloads",
        "resources/spacedock_spacewarp_bepinex.csv"
    )
    download_github_releases(access_token, "SpaceWarpDev", "SpaceWarp", "resources/github_releases.csv")
    find_total_downloads([
        "resources/spacedock_spacewarp.csv",
        "resources/spacedock_spacewarp_bepinex.csv",
        "resources/github_releases.csv"
    ])
    print_total_downloads()
    create_bar_chart()
    create_pie_chart()


if __name__ == '__main__':
    main("YOUR GITHUB ACCESS TOKEN HERE")
