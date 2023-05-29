import os
import time
import requests

from pyrogram.errors.exceptions.bad_request_400 import (MessageIdInvalid,
                                                        MessageNotModified)
from pyrogram.types import Message

from .. import data, doc_thumb, download_dir, upload_doc
from .ffmpeg import encode, get_duration, get_thumbnail
from .progress import progress_for_pyrogram
from .utils import output


async def on_task_complete():
    del data[0]
    if len(data) > 0:
        await handle_task(data[0])


async def handle_task(message: Message):
    try:
        msg = await message.reply_text("<code>Processing video...</code>")
        c_time = time.time()

        # Check if the message contains a valid video file or a URL
        if message.video:
            # Process video file
            filepath = await message.download(
                file_name=download_dir,
                progress=progress_for_pyrogram,
                progress_args=("Downloading...", msg, c_time)
            )
        elif message.text and message.text.startswith("http"):
            # Process video from URL
            filepath = await download_video_from_url(message.text)
        else:
            await msg.edit_text("<code>Invalid video file or URL.</code>")
            return

        print(f'[Download]: {filepath}')
        await msg.edit_text('<code>Encoding...</code>')
        new_file = await encode(filepath)
        if new_file:
            await msg.edit_text("<code>Video Encoded, getting metadata...</code>")
            await handle_upload(new_file, message, msg)
            await msg.edit_text('Video Encoded Successfully!')
        else:
            await message.reply_text("<code>Something went wrong while encoding your file.</code>")
        os.remove(filepath)
    except MessageNotModified:
        pass
    except MessageIdInvalid:
        await msg.edit_text('Download Cancelled!')
    except Exception as e:
        print(f'[Error]: {e}')
        await msg.edit_text(f"<code>{e}</code>")
    await on_task_complete()


async def handle_upload(new_file, message, msg):
    print(f'[Upload]: {new_file}')
    # Variables
    user_id = message.from_user.id
    c_time = time.time()
    filename = os.path.basename(new_file)
    duration = get_duration(new_file)
    thumb = os.path.join(str(user_id), 'thumbnail.jpg')
    height = 720
    width = 1280
    if not os.path.isfile(thumb):
        thumb = get_thumbnail(new_file, download_dir, duration / 4)
    # Upload File
    if upload_doc:
        if doc_thumb:
            thumb = thumb
        else:
            thumb = None
        await message.reply_document(
            new_file,
            thumb=thumb,
            caption=filename,
            reply_markup=output,
            parse_mode=None,
            progress=progress_for_pyrogram,
            progress_args=("Uploading ...", msg, c_time)
        )
    else:
        await message.reply_video(
            new_file,
            supports_streaming=True,
            parse_mode=None,
            reply_markup=output,
            caption=filename,
            thumb=thumb,
            duration=duration,
            width=width,
            height=height,
            progress=progress_for_pyrogram,
            progress_args=("Uploading ...", msg, c_time)
        )
    os.remove(new_file)


async def download_video_from_url(url):
    filename = os.path.join(download_dir, f"{int(time.time())}.mp4")

    response = requests.get(url, stream=True)
    with open(filename, "wb") as file:
        for chunk in response.iter_content(chunk_size=8192):
            file.write(chunk)

    return filename
