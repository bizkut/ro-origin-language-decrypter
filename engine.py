# coding=utf-8
import hashlib
import os


def database_read_len(content: bytearray, payload: dict) -> int:
    size = database_read_byte(1, content, payload)
    if size > 127:
        size += (database_read_byte(1, content, payload) - 1) * 128
    return size


def database_read_string(content: bytearray, payload: dict) -> str:
    str_len = database_read_len(content, payload)
    curr = payload["pos"]
    end = payload["pos"] + str_len

    # adjust payload
    payload["pos"] += str_len

    # output
    return content[curr:end].decode("utf-8")


def database_read_byte(size: int, content: bytearray, payload: dict) -> int:
    """ Read n-bytes and return as int in little endian order.

    Args:
        size (int): Size of the bytes to read
        content (bytearray): Content
        payload (dict): Payload

    Returns:
        int: value of the read n-bytes.
    """
    curr = payload["pos"]
    end = payload["pos"] + size

    # adjust payload size
    payload["pos"] += size

    # save output
    return int.from_bytes(content[curr:end], byteorder="little")


def database_read(file: str) -> list:
    """ Read a language file (*.robytes) for Ragnarok Origin
    and store them on an array.

    Args:
        file (str): Full path for the *.robytes file

    Returns:
        list: Decrypted *.robytes file
    """
    with open(file, "rb") as fh:
        payload = {"pos": 0, "bytes": bytearray()}
        content = bytearray(fh.read())
        container = list()

        total_entry = database_read_byte(4, content, payload)
        for i in range(total_entry):
            index = database_read_byte(4, content, payload)
            text = database_read_string(content, payload)
            container.append({"_id_": index, "text": text})

        return container


def database_build_up(blob_dict: dict) -> bytearray:
    """Build the language database based on the dictionary provided.
    Dictionary format: {"id (int form)": "translated_text (str form)"}.

    Args:
        blob_dict (dictionary): Dictionary to be constructed.

    Returns:
        bytearray: byte array blob ready to be written in a *.robytes file.
    """

    # Iterate each key and value
    container = bytearray()
    for index, text in blob_dict.items():
        # encode texts
        roo_index = index
        roo_text = text.replace("\\n", "\n").encode("utf-8")
        roo_text_len = len(roo_text)

        roo_padding = int(roo_text_len / 128)
        if roo_padding > 0:
            # adjust string len
            roo_text_len -= 128 * (roo_padding - 1)
            # populate container
            container.extend(roo_index.to_bytes(4, "little"))
            container.extend(roo_text_len.to_bytes(1, "little"))
            container.extend(roo_padding.to_bytes(1, "little"))
            container.extend(roo_text)
        else:
            # populate container
            container.extend(roo_index.to_bytes(4, "little"))
            container.extend(roo_text_len.to_bytes(1, "little"))
            container.extend(roo_text)

    # append total item count at the first 4 bytes
    total_count = len(blob_dict)
    container[0:0] = total_count.to_bytes(4, "little")

    # return container
    return container


def patch_file_list(file_list_path: str, robyte_path: str):
	robyte_base_name = os.path.basename(robyte_path)
	robyte_sha1 = ""
	robyte_file_size = 0

	# Open *.robyte to get file size and sha1
	with open(robyte_path, "rb") as fh:
		robyte_content = fh.read()
		robyte_sha1 = hashlib.sha1(robyte_content).hexdigest()
		robyte_file_size = len(robyte_content)

	# Open __file__list__ for patching
	with open(file_list_path, "r+b") as fh:
		content = fh.read()
		pos = content.find(str.encode(robyte_base_name))
		if pos > -1:
			# go to offset
			fh.seek(pos)

			# start patching
			container = bytearray()
			container.extend(robyte_base_name.encode("utf-8"))
			container.extend(robyte_file_size.to_bytes(8, 'little'))
			container.extend(b"\x28")
			container.extend(robyte_sha1.encode("utf-8"))

			# write back the changes
			fh.write(container)

	print("[*] Done patching!")
