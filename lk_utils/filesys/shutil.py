import os
import shutil
import sys
import typing as t
import urllib.request
import zipfile
from collections import namedtuple
from datetime import datetime
from zipfile import ZipFile
from zipfile import ZipInfo
from . import main
from .finder import findall_dirs
from .finder import findall_files
from .main import IS_WINDOWS  # noqa
from .main import abspath
from .main import basename
from .main import dirname
from .main import exist
from .main import real_exist
from .main import xpath
from ..subproc import run_cmd_args
from ..textwrap import dedent

__all__ = [
    'ProgressItem',
    'clone_tree',
    'copy_file',
    'copy_tree',
    'download',
    'make_dir',
    'make_dirs',
    'make_file',
    'make_link',
    'make_links',
    'make_shortcut',
    'move',
    'move_file',
    'move_tree',
    'remove',
    'remove_file',
    'remove_tree',
    'unzip',
    'unzip_file',
    'zip',
    'zip_dir',
]

ProgressItem = namedtuple('ProgressItem', 'total index percent text')
_IS_PYTHON_314_OR_HIGHER = sys.version_info >= (3, 14)


class T:
    AnyProgress = t.Optional[t.Union[t.Callable[[ProgressItem], None], bool]]
    CompressionLevel = t.Literal['fast', 'normal', 'maximum']
    OverwriteScheme = t.Optional[bool]
    ReportProgress = t.Optional[t.Callable[[int, int, str], None]]


def clone_tree(src: str, dst: str, overwrite: T.OverwriteScheme = None) -> None:
    if exist(dst):
        if any(os.listdir(dst)):
            if _overwrite(dst, overwrite):
                os.mkdir(dst)
            else:
                return
    else:
        os.mkdir(dst)
    for d in findall_dirs(src):
        dp_o = f'{dst}/{d.relpath}'
        if not exist(dp_o):
            os.mkdir(dp_o)


def copy_file(
    src: str,
    dst: str,
    overwrite: T.OverwriteScheme = None,
    reserve_metadata: bool = False,
) -> None:
    if exist(dst) and not _overwrite(dst, overwrite):
        return
    if reserve_metadata:
        shutil.copy2(src, dst)
    else:
        shutil.copyfile(src, dst)


def copy_tree(
    src: str,
    dst: str,
    overwrite: T.OverwriteScheme = None,
    symlinks: bool = False,
    reserve_metadata: bool = True,
) -> None:
    if exist(dst) and not _overwrite(dst, overwrite):
        return
    shutil.copytree(
        _safe_long_path(src),
        _safe_long_path(dst),
        copy_function=shutil.copy2 if reserve_metadata else shutil.copy,
        symlinks=symlinks,
    )


def download(
    url: str,
    path: str,
    extract: bool = False,
    keep_file: bool = False,
    progress: T.AnyProgress = None,
    overwrite: T.OverwriteScheme = None,
) -> None:
    """
    params:
        keep_file: whether to keep zip file after extracting.
    """
    if exist(path) and not _overwrite(path, overwrite):
        return

    url = url.replace(' ', '%20')

    # fmt: off
    _report: T.ReportProgress
    if progress is True:
        def _report(count: int, block_size: int, total_size: int) -> None:
            _show_progress_in_console_1(total_size, block_size * count)
    elif progress:
        def _report(count: int, block_size: int, total_size: int) -> None:
            progress(
                ProgressItem(
                    total_size,
                    block_size * count,
                    min((1.0, block_size * count / total_size)),
                    '',
                )
            )
    else:
        _report = None
    # fmt: on

    if extract:
        assert url.endswith(('.zip', '.7z'))
        #   if assertion error, a workaround is setting `extract=False` then
        #   using `unzip_file()` function afterwards.
        ext = url.rsplit('.', 1)[-1]
        temp_file = '{}.tmp.{}'.format(path, ext)
        urllib.request.urlretrieve(url, temp_file, _report)
        unzip_file(temp_file, path)
        if not keep_file:
            remove_file(temp_file)
    else:
        urllib.request.urlretrieve(url, path, _report)


def make_dir(dst: str) -> None:
    if not exist(dst):
        os.mkdir(dst)


def make_dirs(dst: str) -> None:
    os.makedirs(dst, exist_ok=True)


def make_file(dst: str) -> None:
    open(dst, 'w').close()


def make_link(src: str, dst: str, overwrite: T.OverwriteScheme = None) -> str:
    """
    ref: https://blog.walterlv.com/post/ntfs-link-comparisons.html
    """
    src, dst = abspath(src), abspath(dst)

    assert real_exist(src), src
    if exist(dst):
        if overwrite is True:  # noqa
            if real_exist(dst) and os.path.samefile(src, dst):
                return dst
            else:
                remove(dst)
        elif overwrite is False:
            raise FileExistsError(dst)
        elif overwrite is None:
            return dst

    if IS_WINDOWS:
        if main.system_privileged is True:
            os.symlink(src, dst, target_is_directory=os.path.isdir(src))
        elif main.system_privileged is False:
            _make_link_fallback(src, dst)
        else:  # None type. only first-time calling reaches this case.
            try:
                os.symlink(src, dst, target_is_directory=os.path.isdir(src))
            except OSError as e:
                # print(':v8p', e)
                if 'WinError 1314' in str(e):
                    # https://docs.python.org/3/library/os.html#os.symlink
                    print(':pv6', 'fallback symlink under low privileges')
                    main.system_privileged = False
                    _make_link_fallback(src, dst)
                    return dst
                raise e
            else:
                main.system_privileged = True

    return dst


def _make_link_fallback(src: str, dst: str) -> None:
    """
    this function doesn't require administrative privileges.
    note: `src` and `dst` must be absolute paths.
    related:
        https://docs.python.org/3/library/os.html#os.symlink
        https://discuss.python.org/t/add-os-junction-pathlib-path-junction-to
        /50394
    """
    src = src.replace('/', '\\')
    dst = dst.replace('/', '\\')
    if os.path.isdir(src):  # directory junction for dirs
        run_cmd_args(('mklink', '/J', dst, src), shell=True)
    else:  # hard link for files
        run_cmd_args(('mklink', '/H', dst, src), shell=True)


def make_links(
    src: str,
    dst: str,
    names: t.Optional[t.List[str]] = None,
    overwrite: T.OverwriteScheme = None,
) -> t.List[str]:
    out = []
    for n in names or os.listdir(src):
        out.append(make_link(f'{src}/{n}', f'{dst}/{n}', overwrite))
    return out


def make_shortcut(
    src: str, dst: str = '', overwrite: T.OverwriteScheme = None
) -> None:
    """
    use batch script to create shortcut, no pywin32 required.

    params:
        dst:
            if not given, will create a shortcut in the same folder as `src`, -
            with the same base name.
            trick: use "<desktop>" to create a shortcut on the desktop.

    refs:
        https://superuser.com/questions/455364/how-to-create-a-shortcut
        -using-a-batch-script
        https://www.blog.pythonlibrary.org/2010/01/23/using-python-to-create
        -shortcuts/
    """
    assert exist(src) and not src.endswith('.lnk')
    if dst:
        assert dst.endswith('.lnk')
        if '<desktop>' in dst:
            dst = dst.replace('<desktop>', os.path.expanduser('~/Desktop'))
    else:
        dst = os.path.splitext(os.path.basename(src))[0] + '.lnk'

    if exist(dst) and not _overwrite(dst, overwrite):
        return
    if not IS_WINDOWS:
        raise NotImplementedError

    vbs = xpath('./_temp_shortcut_generator.vbs')
    with open(vbs, 'w') as f:
        f.write(
            dedent(
                """
            Set objWS = WScript.CreateObject("WScript.Shell")
            lnkFile = "{file_o}"
            Set objLink = objWS.CreateShortcut(lnkFile)
            objLink.TargetPath = "{file_i}"
            objLink.Save
            """
            ).format(
                file_i=src.replace('/', '\\'),
                file_o=dst.replace('/', '\\'),
            )
        )
    run_cmd_args('cscript', '/nologo', vbs)
    os.remove(vbs)


# def merge_tree(src: str, dst: str, overwrite: bool = False) -> None:
#     if overwrite:  # TODO
#         raise NotImplementedError
#     src_dirs = frozenset(x.relpath for x in findall_dirs(src))
#     src_files = frozenset(x.relpath for x in findall_files(src))
#     dst_dirs = frozenset(x.relpath for x in findall_dirs(dst))
#     dst_files = frozenset(x.relpath for x in findall_files(dst))
#     # TODO


def move(src: str, dst: str, overwrite: T.OverwriteScheme = None) -> None:
    if exist(dst) and not _overwrite(dst, overwrite):
        return
    shutil.move(src, dst)


move_file = move
move_tree = move


def remove(dst: str) -> None:
    if os.path.isfile(dst):
        os.remove(dst)
    elif main.islink(dst):
        os.unlink(dst)
    elif os.path.isdir(dst):
        shutil.rmtree(dst)
    else:
        raise Exception('inexistent or invalid path type', dst)


def remove_file(dst: str) -> None:
    if os.path.isfile(dst):
        os.remove(dst)
    elif main.islink(dst):
        os.unlink(dst)
    else:
        raise Exception('inexistent or invalid path type', dst)


def remove_tree(dst: str) -> None:
    if main.islink(dst):
        os.unlink(dst)
    elif os.path.isdir(dst):
        shutil.rmtree(dst)
    else:
        raise Exception('inexistent or invalid path type', dst)


rename = move


def zip_dir(
    src: str,
    dst: str = '',
    overwrite: T.OverwriteScheme = None,
    progress: T.AnyProgress = None,
    compression_level: T.CompressionLevel = 'normal',
    keep_empty_folders: bool = True,
    # bandizip_command_line_tool: str = '',
    **zip_options,
) -> str:
    """
    ref: https://likianta.blog.csdn.net/article/details/126710855
    params:
        dst:
            if not given, will use `src + '.zip'`.
            if ends with `.zip`, `.7z`, `.tar.zst`, will use it as is.
            additionally, if `dst` is literally one of
            ('.zip', '.7z', '.tar.zst'), will create `src + dst`.
        bandizip_command_line_tool: a path to `<bandizip_software>/bc.exe`.
    """
    if dst:
        if dst in ('.zip', '.7z', '.tar.zst'):
            dst = src + dst
        else:
            assert dst.endswith(('.zip', '.7z', '.tar.zst'))
    else:
        dst = src + '.zip'
    if exist(dst) and not _overwrite(dst, overwrite):
        return dst

    # fmt: off
    _report: T.ReportProgress
    if progress is True:
        _report = _show_progress_in_console_2
    elif progress:
        def _report(total: int, index: int, name: str) -> None:
            progress(
                ProgressItem(total, index, min((1.0, index / total)), name)
            )
    else:
        _report = None
    # fmt: on

    if dst.endswith('.zip'):
        top_name = basename(src)
        todo_dirs = tuple(findall_dirs(src))
        todo_files = tuple(findall_files(src))
        total = len(todo_dirs) + len(todo_files)

        # https://chatgpt.com/share/69f010ae-553c-8320-8e88-00cb37b1b409
        zip_options = {
            'compression': (
                # choice explanation:
                #   python 3.14+: always ZIP_ZSTANDARD
                #   else:
                #       fast: ZIP_STORED
                #       normal: ZIP_DEFLATED
                #       maximum: ZIP_DEFLATED
                _IS_PYTHON_314_OR_HIGHER
                and zipfile.ZIP_ZSTANDARD
                or compression_level == 'fast'
                and zipfile.ZIP_STORED
                or zipfile.ZIP_DEFLATED
            ),
            'compresslevel': (
                # choice explanation:
                #   ZIP_ZSTANDARD: -5 for fast, 3 for normal, 19 for maximum.
                #   ZIP_STORED: value has no effect.
                #   ZIP_DEFLATED: 1 for fast, 6 for normal, 9 for maximum.
                _IS_PYTHON_314_OR_HIGHER
                and (
                    compression_level == 'fast'
                    and -5
                    or compression_level == 'normal'
                    and 3
                    or compression_level == 'maximum'
                    and 19
                )
                or (
                    compression_level == 'fast'
                    and 1
                    or compression_level == 'normal'
                    and 6
                    or compression_level == 'maximum'
                    and 9
                )
            ),
            **zip_options,
        }

        with ZipFile(dst, 'w', **zip_options) as handle:  # type: ignore
            handle.write(src, arcname=top_name)
            i = 0
            for d in todo_dirs:
                i += 1
                if _report:
                    _report(total, i, d.name)
                handle.write(
                    d.path, arcname='{}/{}'.format(top_name, d.relpath)
                )
            for f in todo_files:
                i += 1
                if _report:
                    _report(total, i, f.name)
                handle.write(
                    f.path, arcname='{}/{}'.format(top_name, f.relpath)
                )

    elif dst.endswith('.7z'):
        import py7zr  # `pip install lk-utils[zip]` or `pip install py7zr`

        top_name = basename(src)
        todo_paths = tuple(findall_dirs(src)) + tuple(findall_files(src))
        total = len(todo_paths)

        # https://chatgpt.com/share/69f01d60-62a4-8320-aee3-b7ef6f390ddf
        zip_options = {
            'filters': [
                {
                    'id': py7zr.FILTER_LZMA2,
                    'preset': (
                        compression_level == 'fast'
                        and 1
                        or compression_level == 'normal'
                        and 6
                        or compression_level == 'maximum'
                        and 9
                    ),
                    # 'dict_size': 1 << 29,  # 512MB
                }
            ],
            **zip_options,
        }

        with py7zr.SevenZipFile(
            dst,
            'w',
            **zip_options,  # type: ignore
        ) as handle:
            handle.write(src, arcname=top_name)
            for i, p in enumerate(todo_paths, 1):
                if _report:
                    _report(total, i, p.name)
                handle.write(
                    os.path.realpath(p.path),
                    arcname='{}/{}'.format(top_name, p.relpath),
                )

    elif dst.endswith('.tar.zst'):
        # https://chatgpt.com/share/69dde78d-8348-8321-b90d-0efc090f6b4f
        import tarfile

        # from compression import zstd  # TODO
        import zstandard as zstd  # pip install zstandard

        top_name = basename(src)
        todo_files = tuple(findall_files(src))
        if keep_empty_folders:
            all_dirs = frozenset((x.relpath for x in findall_dirs(src)))
            dirs_not_empty = frozenset(
                (
                    x.relpath.rsplit('/', 1)[0]
                    for x in todo_files
                    if '/' in x.relpath
                )
            )
            todo_dirs = sorted(all_dirs - dirs_not_empty)
        else:
            todo_dirs = ()
        total = len(todo_dirs) + len(todo_files)
        empty = xpath('.empty')

        with open(dst, 'wb') as file_out:
            with zstd.ZstdCompressor(**zip_options).stream_writer(
                file_out
            ) as compressor:
                with tarfile.open(fileobj=compressor, mode='w|') as tar:
                    tar.add(src, arcname=basename(src))
                    i = 0
                    for f in todo_files:
                        i += 1
                        if _report:
                            _report(total, i, f.name)
                        if os.path.islink(f.path):
                            full_path = os.path.realpath(f.path)
                        else:
                            full_path = f.path
                        tar.add(
                            full_path,
                            arcname='{}/{}'.format(top_name, f.relpath),
                        )
                    if keep_empty_folders:
                        for d in todo_dirs:
                            i += 1
                            if _report:
                                _report(
                                    total, i, d.rsplit('/', 1)[-1] + '/.empty'
                                )
                            tar.add(
                                empty,
                                arcname='{}/{}'.format(top_name, d + '/.empty'),
                            )

    else:
        raise Exception('no handler to compress this file type', dst)

    if _report and progress is True:
        print('', ':s2')
    return dst


def unzip_file(
    src: str,
    dst: str = '',
    overwrite: T.OverwriteScheme = None,
    progress: T.AnyProgress = None,
    rewrite_top_name: bool = True,
    reserve_file_mtime: bool = True,
    **zip_options,
) -> str:
    assert src.endswith(('.zip', '.7z', '.tar.zst'))
    if not dst:
        dst = (
            src.rsplit('.', 1)[0]
            if src.endswith(('.zip', '.7z'))
            else src.rsplit('.', 2)[0]
        )
    # print(src, dst, overwrite, exist(path_o), ':lvp')
    if exist(dst) and not _overwrite(dst, overwrite):
        return dst
    else:
        dst = dst.replace('\\', '/')

    # fmt: off
    _report: T.ReportProgress
    if progress is True:
        _report = _show_progress_in_console_2
    elif progress:
        def _report(total: int, index: int, name: str) -> None:
            progress(
                ProgressItem(total, index, min((1.0, index / total)), name)
            )
    else:
        _report = None
    # fmt: on

    if src.endswith('.zip'):

        def detect_single_top(handle: ZipFile) -> str:
            top_names = set()
            for name in handle.namelist():
                # print(name, ':vi')
                if name.endswith('/'):
                    if '/' not in name[:-1]:
                        top_names.add(name[:-1])
                elif '/' not in name:
                    return ''
            if len(top_names) == 1:
                return top_names.pop()
            else:
                return ''

        with ZipFile(src, 'r', **zip_options) as handle:
            top_name_i = detect_single_top(handle)
            top_name_o = dirname(dst)
            # print(top_name_i, top_name_o, rewrite_top_name, ':v')
            trim_src_prefix = False
            if top_name_i:
                if top_name_i == top_name_o or rewrite_top_name:
                    trim_src_prefix = True

            todo_dirs: t.Set[str] = set()
            todo_files: t.Set[t.Tuple[str, ZipInfo, int]] = set()
            for relpath in handle.namelist():
                relpath = (
                    relpath[len(top_name_i) + 1 :]
                    if trim_src_prefix
                    else relpath
                )
                if relpath:
                    if relpath.endswith('/'):
                        todo_dirs.add(relpath[:-1])
                    else:
                        info = handle.NameToInfo[relpath]
                        time = int(datetime(*info.date_time).timestamp())
                        todo_files.add((relpath, info, time))
                        if '/' in relpath:
                            todo_dirs.add(relpath.rsplit('/', 1)[0])
            total = len(todo_dirs) + len(todo_files)

            # -- make dirs
            os.mkdir(dst)
            i = 0
            for relpath in sorted(todo_dirs):
                if _report:
                    i += 1
                    _report(total, i, relpath)
                os.makedirs(dst + '/' + relpath, exist_ok=True)

            # -- dump files
            for relpath, info, time in sorted(todo_files, key=lambda x: x[0]):
                if _report:
                    i += 1
                    _report(total, i, relpath)
                with handle.open(info) as f_reader:
                    with open(dst + '/' + relpath, 'wb') as f_writer:
                        shutil.copyfileobj(f_reader, f_writer)
                if reserve_file_mtime:
                    os.utime(dst + '/' + relpath, (time, time))

    elif src.endswith('.7z'):
        # https://chatgpt.com/share/69f042ab-03c0-8323-8187-70f87711119c
        from pathlib import Path
        from py7zr import SevenZipFile
        from py7zr.helpers import filetime_to_dt
        # from py7zr.callbacks import ExtractCallback

        def detect_single_top(handle: SevenZipFile) -> str:
            top_names = set()
            for f in handle.files:
                if f.is_directory:
                    if '/' not in f.filename.rstrip('/'):
                        top_names.add(f.filename.rstrip('/'))
                elif '/' not in f.filename:
                    return ''
            if len(top_names) == 1:
                return top_names.pop()
            else:
                return ''

        with SevenZipFile(src, 'r', **zip_options) as handle:
            top_name_i = detect_single_top(handle)
            top_name_o = dirname(dst)
            trim_src_prefix = False
            if top_name_i:
                if top_name_i == top_name_o or rewrite_top_name:
                    trim_src_prefix = True
            print(top_name_i, top_name_o, trim_src_prefix, ':v')

            # --- a
            # reimplementation of `py7zr.SevenZipFile.extractall()`,
            # `py7zr.py7zr.Worker.extract_single()`.

            worker = handle.worker
            assert worker.header.main_streams.unpackinfo.numfolders == 1
            src_start = worker.src_start
            src_end = (
                src_start
                + worker.header.main_streams.packinfo.packpositions[-1]
            )
            # print(src_start, src_end, ':v')
            handle.fp.seek(src_start)

            out_root = Path(dst)
            total = len(handle.files)
            just_checks = []

            for i, f in enumerate(handle.files, 1):
                if _report:
                    _report(total, i, f.filename)

                if trim_src_prefix:
                    if f.filename == top_name_i:
                        continue
                    else:
                        assert f.filename.startswith(top_name_i + '/')
                relpath = (
                    f.filename[len(top_name_i) + 1 :]
                    if trim_src_prefix
                    else f.filename
                )
                assert relpath

                # print(
                #     i,
                #     f.filename,
                #     # f.emptystream,
                #     src_start,
                #     src_end,
                #     f.compressed,
                #     f.uncompressed,
                #     # f.folder.get_decompressor(f.compressed),
                #     ':lv',
                # )
                # assert f.compressed is not None, f.filename

                worker._check(handle.fp, just_checks, src_end)
                just_checks.clear()

                out_path = out_root / relpath
                if f.is_directory:
                    out_path.mkdir(parents=True, exist_ok=True)
                elif f.is_socket or f.is_symlink or f.is_junction:
                    raise Exception(f.filename)
                else:
                    out_path.parent.mkdir(parents=True, exist_ok=True)
                    with out_path.open('wb') as f_writer:
                        crc32 = worker.decompress(
                            handle.fp,
                            f.folder,
                            f_writer,
                            f.uncompressed,
                            f.compressed or f.uncompressed,
                            src_end,
                        )
                        f_writer.seek(0)
                        if f.crc32 and f.crc32 != crc32:
                            raise Exception(f.filename, crc32, f.crc32)
                    if reserve_file_mtime and f.lastwritetime:
                        mtime = int(filetime_to_dt(f.lastwritetime).timestamp())
                        os.utime(str(out_path), (mtime, mtime))

            # resolve empty directories.
            # for f in handle.files:
            #     if f.is_directory:
            #         if relpath := (
            #             f.filename[len(top_name_i) + 1 :]
            #             if trim_src_prefix
            #             else f.filename
            #         ):
            #             print('post fix empty folder', relpath, ':v')
            #             out_path = '{}/{}'.format(dst, relpath)
            #             if not os.path.exists(out_path):
            #                 os.makedirs(out_path)

            # --- b

            # # https://github.com/miurahr/py7zr/issues/526#issue-1816063884
            # class MyCallback(ExtractCallback):
            #     def __init__(
            #         self,
            #         total_bytes: int,
            #         report_hook: t.Callable[[int, int, str], None],
            #     ) -> None:
            #         self._total = total_bytes
            #         self._report_hook = report_hook

            #     def report_update(self, decompressed_bytes: str) -> None:
            #         self._report_hook(self._total, int(decompressed_bytes), '')

            #     # --------------------------------------------------------------

            #     def report_start_preparation(self) -> None:
            #         pass

            #     def report_start(
            #         self, processing_file_path: str, processing_bytes: str
            #     ) -> None:
            #         pass

            #     def report_end(
            #         self, processing_file_path: str, wrote_bytes: str
            #     ) -> None:
            #         pass

            #     def report_warning(self, message: str) -> None:
            #         pass

            #     def report_postprocess(self) -> None:
            #         pass

            # if progress is True:
            #     _callback = MyCallback(
            #         handle.archiveinfo().uncompressed,
            #         _show_progress_in_console_1,
            #     )
            # elif progress:
            #     _callback = MyCallback(
            #         handle.archiveinfo().uncompressed,
            #         lambda total, curr, desc: ProgressItem(
            #             total, curr, min((1.0, curr / total)), ''
            #         ),
            #     )
            # else:
            #     _callback = None

            # if trim_src_prefix:
            #     dst_temp = dst + '_(7z_temp_extracted)'
            #     handle.extractall(dst_temp, callback=_callback)
            #     shutil.move(dst_temp + '/' + top_name_i, dst)
            #     shutil.rmtree(dst_temp)
            # else:
            #     handle.extractall(dst, callback=_callback)
            # if reserve_file_mtime:
            #     for f in handle.files:
            #         if f.lastwritetime:
            #             path = '{}/{}'.format(
            #                 dst,
            #                 f.filename[len(top_name_i) + 1 :]
            #                 if trim_src_prefix
            #                 else f.filename,
            #             )
            #             time = int(filetime_to_dt(f.lastwritetime).timestamp())
            #             os.utime(path, (time, time))

            # ---

            # todo_dirs: t.Set[str] = set()
            # todo_files: t.Set[t.Tuple[str, ArchiveFile, int]] = set()
            # # todo_files: t.Set[t.Tuple[str, str, int]] = set()
            # for info in handle.files:
            #     name = (
            #         info.filename[len(top_name_i) + 1 :]
            #         if trim_src_prefix
            #         else info.filename
            #     )
            #     if info.is_directory:
            #         todo_dirs.add(name.rstrip('/'))
            #     else:
            #         time = (
            #             int(filetime_to_dt(info.lastwritetime).timestamp())
            #             if info.lastwritetime
            #             else 0
            #         )
            #         todo_files.add((name, info, time))
            #         if '/' in name:
            #             todo_dirs.add(name.rsplit('/', 1)[0])
            # total = len(todo_dirs) + len(todo_files)

            # # -- make dirs
            # os.mkdir(dst)
            # os.mkdir(temp_dir := dst + '/._temp_7z_extracted')
            # i = 0
            # for relpath in sorted(todo_dirs):
            #     if _report:
            #         i += 1
            #         _report(total, i, relpath)
            #     os.makedirs(dst + '/' + relpath, exist_ok=True)

            # # def _skip_check(*_, **__):
            # #     pass

            # # setattr(handle.worker, '_check', _skip_check)

            # # -- dump files
            # for relpath, info, time in sorted(todo_files, key=lambda x: x[0]):
            #     if _report:
            #         i += 1
            #         _report(total, i, relpath)
            #     # -- c
            #     # handle.extract(targets=[info.filename], path=temp_dir)
            #     # shutil.move(temp_dir + '/' + info.filename, dst + '/' + relpath)
            #     # -- d
            #     # data = handle.read((key,))[key]
            #     # f_reader = t.cast(t.BinaryIO, info.data())
            #     # if f_reader is None:
            #     #     raise Exception(relpath, info)
            #     # with open(dst + '/' + relpath, 'wb') as f_writer:
            #     #     f_writer.write(f_reader.read())
            #     # -- e: minimal implementation of `py7zr.SevenZipFile.extract()`
            #     file_o = Path(dst + '/' + relpath)
            #     handle.worker.register_filelike(info.id, file_o)
            #     handle.worker.extract(handle.fp, file_o.parent, parallel=False)
            #     if reserve_file_mtime and time:
            #         os.utime(dst + '/' + relpath, (time, time))
            # shutil.rmtree(temp_dir)

    else:
        raise NotImplementedError

    if _report and progress is True:
        print('', ':s2')
    return dst


zip = zip_dir
unzip = unzip_file


def _overwrite(path: str, scheme: T.OverwriteScheme) -> bool:
    """
    params:
        scheme:
            True: overwrite
            False: no overwrite, and raise an FileexistError
            None: no overwrite, no error (skip)
    returns: bool
        True menas "can do overwrite".
    """
    if scheme is None:
        return False
    elif scheme is True:  # noqa
        remove(path)
        return True
    else:  # raise error
        raise FileExistsError(path)


def _safe_long_path(path: str) -> str:
    """
    avoid path limit error in windows.
    ref: docs/devnote/issues-summary-202401.zh.md
    """
    if IS_WINDOWS:
        return '\\\\?\\' + os.path.abspath(path)
    return path


def _show_progress_in_console_1(
    total: float, current: float, desc: str = ''
) -> None:
    """
    size-based progress bar.
    """
    prog = current / total
    print(
        ':s1r',
        '[red]{}[/][bright_black]{}[/] {}'.format(
            '-' * round(prog * 60),
            '-' * (60 - round(prog * 60)),
            desc and '{} ({:.2%})'.format(desc, prog) or '{:.2%}'.format(prog),
        ),
        end='\r',
    )


def _show_progress_in_console_2(
    total: t.Union[float, int], current: t.Union[float, int], desc: str = ''
) -> None:
    """
    count-based progress bar.
    """
    prog = current / total
    print(
        ':s1r',
        '\\[{}/{}] [red]{}[/][bright_black]{}[/] {}'.format(
            current,
            total,
            '-' * round(prog * 60),
            '-' * (60 - round(prog * 60)),
            desc and '{} ({:.2%})'.format(desc, prog) or '{:.2%}'.format(prog),
        ),
        end='\r',
    )
