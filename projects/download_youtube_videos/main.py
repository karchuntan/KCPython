import os
import click
import logging

from pytube import YouTube
from moviepy.editor import *


@click.group
@click.option(
    "-d",
    "--debug",
    "debug",
    is_flag=True,
    default=False,
    show_default=True,
    help="Activate debugging levels information",
)
def cli_grouping(debug) -> None:
    logging.basicConfig(
        level=logging.DEBUG if debug else logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler("log.log", mode="a"),
        ],
    )


@cli_grouping.command()
@click.option(
    "-l",
    "--link",
    "youtube_links",
    required=True,
    multiple=True,
    help="Youtube link to be downloaded",
)
@click.option(
    "-c",
    "--convert",
    "convert",
    is_flag=True,
    default=False,
    show_default=True,
    help="Convert video (MP4) to audio format (MP3)",
)
@click.pass_context
def download(ctx, youtube_links: tuple, convert: bool) -> None:
    """
    Download Youtube video in MP4 format from Youtube link

    Args:
        youtube_links (tuple): Tuple of Youtube links to be downloaded

    Returns:
        None
    """
    logger = logging.getLogger("youtube_download")
    for link in youtube_links:
        youtube_obj = YouTube(link)
        youtube_obj = youtube_obj.streams.get_highest_resolution()
        logger.info(f"Extracting and downloading Youtube video: {youtube_obj.title}")
        try:
            youtube_obj.download(
                output_path="mp4", filename=youtube_obj.default_filename
            )
            if convert:
                ctx.invoke(
                    convert_mp4_to_mp3,
                    mp4_files=(os.path.join("mp4", youtube_obj.default_filename),),
                )
        except Exception as e:
            logger.error(f"Fail to download this youtube video '{link}': {e}")


@cli_grouping.command(name="convert")
@click.option(
    "-f",
    "--file",
    "mp4_files",
    required=True,
    multiple=True,
    help="MP4 file path to be converted to MP3 file format",
)
def convert_mp4_to_mp3(mp4_files: tuple) -> None:
    """
    Convert MP4 file to MP3 file format

    Args:
        mp4_files (tuple): Tuple of MP4 files to be converted to MP3 file format

    Returns:
        None
    """
    folder_name = "mp3"
    logger = logging.getLogger("convert_mp4_to_mp3")
    if os.path.exists(folder_name) == False:
        os.mkdir(folder_name)

    for file in mp4_files:
        if os.path.exists(file):
            mp4_video = VideoFileClip(file)
            try:
                logger.info(f"Extracting audio from '{file}'")
                mp4_video.audio.write_audiofile(
                    mp4_video.filename.replace("mp4", "mp3")
                )
            except Exception as e:
                logger.error(f"Fail to convert this file '{file}' to mp3 format: {e}")
        else:
            logger.error(f"File: '{file}' does not exists")


if __name__ == "__main__":
    cli_grouping()
