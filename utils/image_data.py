import io

from aiogram.types import BufferedInputFile


async def get_image_data(message, bot):
    image = message.photo[-1]
    file_info = await bot.get_file(image.file_id)

    buffer = io.BytesIO()
    await bot.download_file(file_info.file_path, destination=buffer)
    buffer.seek(0)

    file_bytes = buffer.getvalue()
    file_name = f"{message.message_id}_{image.file_unique_id}.png"
    input_file = BufferedInputFile(file=file_bytes, filename=file_name)
    
    return file_bytes, input_file