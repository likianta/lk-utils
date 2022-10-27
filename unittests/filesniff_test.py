import lk_logger

from lk_utils import filesniff as fs

lk_logger.setup(show_varnames=True)


def test_listing_files():
    print(':l', fs.find_file_paths('../lk_utils'))
    print(':l', fs.find_file_names('../lk_utils'))
    
    print(':i0')
    for fp, fn in fs.find_files('../lk_utils'):
        print(':i', fp, fn)
    
    # -------------------------------------------------------------------------
    print(':d')
    
    print(':l', fs.find_dir_paths('../lk_utils'))
    print(':l', fs.find_dir_names('../lk_utils'))
    
    print(':i0')
    for dp, dn in fs.find_dirs('../lk_utils'):
        print(':i', dp, dn)
    
    # -------------------------------------------------------------------------
    print(':d')
    
    print(':l', fs.findall_file_paths('../lk_utils'))
    print(':l', fs.findall_file_names('../lk_utils'))
    
    print(':i0')
    for fp, fn in fs.findall_files('../lk_utils'):
        print(':i', fp, fn)
    
    # -------------------------------------------------------------------------
    print(':d')
    
    print(':l', fs.findall_dir_paths('../lk_utils'))
    print(':l', fs.findall_dir_names('../lk_utils'))
    
    print(':i0')
    for fp, fn in fs.findall_dirs('../lk_utils'):
        print(':i', fp, fn)
