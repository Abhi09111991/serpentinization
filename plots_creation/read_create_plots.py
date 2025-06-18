import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
import os
from pathlib import Path
import plotly.graph_objs as go
from plotly.subplots import make_subplots
import re


def extract_base_and_suffix(filename):
    match = re.match(r"^(.*?)(\d*)\.txt$", filename)
    if match:
        base_name = match.group(1)
        suffix = match.group(2)
        suffix_num = int(suffix) if suffix else 0
        return (base_name, suffix_num)
    return (filename, 0)


# Custom sort key function
def custom_sort_key(filename):
    base_name, suffix_num = extract_base_and_suffix(filename)
    return (base_name, suffix_num)


def remove_trailing_digit(s):
    return re.sub(r"\d+$", "", s)


def read_create_plots(path_text_files: str, path_for_tables: str) -> Figure:
    """
    :param path_text_files: Provide poth where you saved all the text files
    path_for_tables: save the tables in the folder.

    :return: List of figures which will be used in show_plots later.
    """

    figures = []

    text_file_path = Path(path_text_files)
    tables_path = Path(path_for_tables)
    text_files = os.listdir(text_file_path)

    text_files = sorted(text_files, key=custom_sort_key)

    # Identify grouped filenames
    grouped_filenames = []
    other_filenames = []

    # Dictionary to track the base names and their counts
    base_name_counts = {}
    for filename in text_files:
        base_name, suffix_num = extract_base_and_suffix(filename)
        if base_name in base_name_counts:
            base_name_counts[base_name].append(filename)
        else:
            base_name_counts[base_name] = [filename]

    # Separate grouped filenames from others
    for base_name, files in base_name_counts.items():
        if len(files) > 1:
            grouped_filenames.extend(files)
        else:
            other_filenames.extend(files)

    # Combine grouped filenames first, then other filenames
    text_files = grouped_filenames + other_filenames

    count = 1
    if len(text_files) < 16:
        fig, axs = plt.subplots(
            len(text_files) // 2, 2, figsize=(10, 10), sharex=True, sharey=True
        )
    else:
        fig, axs = plt.subplots(8, 2, figsize=(10, 10), sharex=True, sharey=True)
    # fig_title = fig.suptitle('Correlation between ground Spectra with USGS standard library ', fontsize=16)
    # fig_title.set_y(0.95)

    for txtfile in text_files:
        with open(text_file_path / txtfile, "r") as file:

            # Read the entire contents of the file
            for _ in range(1):
                next(file)
            columns = [
                line.strip().split(":")[1].strip() for line in file.readlines()[:3]
            ]

        df = pd.read_csv(
            text_file_path / txtfile, sep="\s+", skiprows=4, header=None, names=columns
        )

        df.to_csv(tables_path / "{}.csv".format(txtfile.split(".")[0]), index=False)
        df_temp = df.copy()
        df_filtered = df_temp[
            (df_temp[columns[1]] != 1.0000) & (df_temp[columns[1]] != 0.0000)
        ]
        i = (count - 1) // 2
        j = (count - 1) % 2
        ax = axs[i, j]
        # print(df_filtered.columns[1].split()[0].split('.')[0].capitalize() + " USGS")
        # print(df.columns[2].split('.')[0])

        ax.plot(
            df_filtered[columns[0]],
            df_filtered[columns[1]],
            label="{}".format(
                df_filtered.columns[1].split()[0].split(".")[0][0:-1].capitalize()
                + " USGS"
            ),
            # [0:-1].capitalize()
            color="blue",
        )

        ax.plot(
            df[columns[0]],
            df[columns[2]],
            label="{}".format(df.columns[2].split(".")[0]),
            color="red",
        )
        ax.annotate(
            remove_trailing_digit(txtfile.split(".")[0].capitalize()),
            xy=(400, 0.55),
            xytext=(5, -5),
            textcoords="offset points",
            ha="left",
            va="top",
            fontsize=10,
            fontweight="bold",
        )
        ax.legend(fontsize=8, loc="lower right", bbox_to_anchor=(0.85, 0.01))
        count += 1

    annotations = [
        "a",
        "b",
        "c",
        "d",
        "e",
        "f",
        "g",
        "h",
        "i",
        "j",
        "k",
        "l",
        "m",
        "n",
        "o",
        "p",
        "q",
    ]
    positions = [(0.05, 0.7)] * 16
    for ax, label, pos in zip(axs.flat, annotations, positions):
        ax.text(
            pos[0],
            pos[1],
            label,
            transform=ax.transAxes,
            fontsize=10,
            fontweight="bold",
            va="top",
        )

    plt.subplots_adjust(wspace=0, hspace=0)
    fig.text(0.5, 0.04, "Wavelength(nm)", ha="center", fontsize=16)
    fig.text(0.04, 0.5, "Reflectance", va="center", rotation="vertical", fontsize=16)

    return fig


def read_create_plotly_plots(path_text_files: str, path_for_tables: str) -> go.Figure:
    """

    :param
    path_text_files: Provide poth where you saved all the text files
    path_for_tables: save the tables in the folder

    :return: List of figures which will be used in show_plots later.
    """

    text_file_path = Path(path_text_files)
    tables_path = Path(path_for_tables)
    text_files = os.listdir(text_file_path)
    rows = [1, 1, 2, 2, 3, 3, 4, 4, 5, 5, 6, 6, 7, 7, 8, 8]
    cols = [1, 2, 1, 2, 1, 2, 1, 2, 1, 2, 1, 2, 1, 2, 1, 2]
    combinations = list(zip(rows, cols))
    count = 0
    if len(text_files) < 16:
        fig = make_subplots(
            rows=len(text_files) // 2,
            cols=2,
            shared_xaxes=True,
            shared_yaxes=True,
            column_widths=[0.3, 0.3],
            horizontal_spacing=0.01,
            vertical_spacing=0.01,
        )
    else:
        fig = make_subplots(
            rows=8,
            cols=2,
            shared_xaxes=True,
            shared_yaxes=True,
            column_widths=[0.3, 0.3],
            horizontal_spacing=0.01,
            vertical_spacing=0.01,
        )
    for txtfile in text_files:
        with open(text_file_path / txtfile, "r") as file:

            # Read the entire contents of the file
            for _ in range(1):
                next(file)
            columns = [
                line.strip().split(":")[1].strip() for line in file.readlines()[:3]
            ]

        df = pd.read_csv(
            text_file_path / txtfile, sep="\s+", skiprows=4, header=None, names=columns
        )

        df.to_csv(tables_path / "{}.csv".format(txtfile.split(".")[0]), index=False)
        df_temp = df.copy()
        df_filtered = df_temp[
            (df_temp[columns[1]] != 1.0000) & (df_temp[columns[1]] != 0.0000)
        ]

        fig.add_trace(
            go.Scatter(
                x=df_filtered[columns[0]],
                y=df_filtered[columns[1]],
                name="{}".format(
                    df_filtered.columns[1].split()[0].split(".")[0] + " USGS"
                ),
            ),
            row=combinations[count][0],
            col=combinations[count][1],
        )

        fig.add_trace(
            go.Scatter(
                x=df[columns[0]],
                y=df[columns[2]],
                name="{}".format(df.columns[2].split(".")[0]),
            ),
            row=combinations[count][0],
            col=combinations[count][1],
        )
        fig.add_annotation(
            text=txtfile.split(".")[0],
            x=500,
            y=0.7,
            row=combinations[count][0],
            col=combinations[count][1],
            showarrow=False,
        )

        count += 1
    fig.update_layout(
        height=1500,
        width=1500,
        # title_text="Correlation between ground Spectra with USGS standard library",
        font_size=20,
    )

    fig.update_layout(
        xaxis_title="Wavelength (nm)",
        yaxis_title="Reflectance",
        xaxis=dict(title_standoff=1200, ticklen=10),
        yaxis=dict(title_standoff=20, ticklen=500),
    )

    return fig


if __name__ == "__main__":

    print("IMPORTANT INFORMATION:")
    print("Examples which needs to be supplied inside the functions: " + "\n")
    print(
        "path_text_files: E:\hard rock\Hard Rock Sample -20240612T171500Z-001\Hard Rock Sample\spectroscopy hard sample\sample 2"
    )
    print(
        "path_for_tables: 'E:\\save_plots_txt\\tables' --> where you want to save your tables."
        + "\n"
    )
    print("\n")
    text_file_path = input("Please enter the text file path (Eg: Brucite.txt etc.): ")
    tables_path = input(
        "Please enter the path where you would like to save tables (csv format): "
    )
    plotly_mat = input(
        "Which plots do you need ? Press 1 for matplotlib and 2 for Plolty: "
    )
    file_address = input("Enter the path where you would like to save your file: ")
    file_name = input("Please enter the filename : ")

    plotly_mat_options = [1, 2]
    if int(plotly_mat) not in plotly_mat_options:
        raise ValueError(
            "Please provide either 1 or 2 as an option to proceed. Thank You!"
        )
    else:
        if str(text_file_path) and int(plotly_mat) == 1:
            fig = read_create_plots(
                path_text_files=text_file_path, path_for_tables=tables_path
            )
            fig.savefig(Path(file_address) / f"{file_name}.png")

        elif str(text_file_path) and int(plotly_mat) == 2:
            fig = read_create_plotly_plots(
                path_text_files=text_file_path, path_for_tables=tables_path
            )
            fig.write_html(Path(file_address) / f"{file_name}.html")

    print(f" *** Files are successfully saved at {file_address} *** ")
