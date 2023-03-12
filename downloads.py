import argparse
import os
import urllib.request
import matplotlib.pyplot as plt
import github
import csv

downloads_by_version = {}


def download_spacedock(url, filename):
    if not os.path.exists('resources'):
        os.makedirs('resources')
    with urllib.request.urlopen(url) as response, open(filename, 'wb') as out_file:
        data = response.read()  # read the data from the response
        out_file.write(data)  # write the data to a local file


def download_github_releases(access_token, owner, repo, output_file):
    gh = github.Github(access_token)

    # get the repo
    repo = gh.get_repo(full_name_or_id=f"{owner}/{repo}")

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
    # Loop through each CSV file
    for file_name in csv_files:
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
    # Print out the total downloads by version and sort by version major.minor.patch
    for version, downloads in downloads_by_version.items():
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

    # Set the colors and font styles for the bars and text
    bar_color = '#1f77b4'  # blue
    text_color = '#FFFFFF'  # white
    font_size = 12

    # Calculate the total number of downloads
    total_downloads = sum(download_counts)

    # Create a bar chart using Matplotlib
    plt.bar(versions, download_counts, color=bar_color)
    plt.xlabel('Version', color=text_color, fontsize=font_size)
    plt.ylabel('Downloads', color=text_color, fontsize=font_size)
    plt.title(f'Total Downloads by Version\n{total_downloads:,} total downloads', color=text_color, fontsize=font_size)
    plt.xticks(color=text_color, fontsize=font_size)
    plt.yticks(color=text_color, fontsize=font_size)
    plt.tight_layout()  # to prevent labels from getting clipped

    # Save the pie chart to a file in the out directory
    if not os.path.exists('out'):
        os.makedirs('out')
    plt.savefig('out/bar_chart.png', bbox_inches='tight')

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

    # Set the colors and font styles for the pie chart and text
    pie_colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd']
    text_color = '#FFFFFF'  # white
    font_size = 12

    # Create a pie chart using Matplotlib
    fig, ax = plt.subplots()
    wedges, texts, autotexts = ax.pie(
        significant_counts + [insignificant_count],
        colors=pie_colors + ['#808080'],
        labels=significant_versions + ['Others'],
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
    if not os.path.exists('out'):
        os.makedirs('out')
    plt.savefig('out/pie_chart.png', bbox_inches='tight')

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
    parser = argparse.ArgumentParser()
    parser.add_argument('access_token', help='Your Github access token')
    args = parser.parse_args()

    main(args.access_token)
