from lk_utils import fs

# file operations
fs.copy_file('old.txt', 'new.txt')
fs.move_file('old.txt', 'new.txt')
fs.remove_file('old.txt')

# folder operations
fs.copy_tree('old_folder', 'new_folder')
fs.move_tree('old_folder', 'new_folder')
fs.remove_tree('old_folder')
fs.clone_tree('old_folder', 'new_folder')  # create empty folders

# symlink
fs.make_link('from.txt', 'to.txt')
fs.make_link('from_dir', 'to_dir')

# overwrite if exists
fs.copy_file('old.txt', 'new.txt', overwrite=True)
fs.copy_tree('old_folder', 'new_folder', overwrite=True)
