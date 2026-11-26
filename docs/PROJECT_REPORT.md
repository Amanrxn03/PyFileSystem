# PyFileSystem – Project Report

## Abstract
PyFileSystem is a Python desktop application that demonstrates file-system interfaces and implementation techniques. It combines a controlled Linux file-operation subsystem with an independent virtual file-system simulator. The simulator demonstrates allocation algorithms, directory organization, access methods, free-space management, deletion and permissions without modifying actual disk structures.

## Objectives
1. Demonstrate common file and directory operations.
2. Explain sequential and direct access methods.
3. Implement contiguous, linked and indexed allocation simulations.
4. Track free and occupied blocks using a bitmap.
5. Demonstrate file deletion and block reclamation.
6. Model owner/group/others permissions.
7. Enforce a strict boundary around real Linux file operations.

## System design
The application uses a Tkinter desktop interface. The Windows GUI communicates with a Linux worker in Ubuntu WSL2 for real operations. The worker confines all paths to `~/pyfilesystem_lab/lab_test`. The simulation is a separate Python subsystem whose state is persisted in JSON.

## Modules
- Actual Linux file operations: create, read, append, rename, delete, list, metadata and restricted chmod.
- Allocation: contiguous searches for a consecutive run; linked uses available blocks and models a chain; indexed reserves an index block and data blocks.
- Free space: a bitmap where 0 means free and 1 means occupied.
- Directories: virtual tree hierarchy.
- Access methods: sequential record listing and direct record retrieval/update.
- Permissions: three octal digits represent owner, group and others.
- Deletion: release all blocks referenced by the virtual file and update the bitmap.

## Algorithms
### Contiguous allocation
Search candidate start positions from the first block. Select the first run of the required length whose bitmap entries are all zero. If no run exists, report external fragmentation or insufficient contiguous space.

### Linked allocation
Select the required number of free blocks. The ordered block list represents the chain; a real linked-list implementation may store an explicit next pointer for each block.

### Indexed allocation
Reserve one index block in addition to data blocks. The allocation record stores the reserved index block followed by the data block references.

### Bitmap
Each disk block has one bit of state. Allocation changes free entries to occupied; deletion resets the file's entries to free.

## Safety
Actual operations are restricted to a dedicated WSL lab directory. Paths are relative, traversal is rejected, symbolic links are rejected, file creation is exclusive, and safe permission profiles are used. Simulation metadata is persisted separately as JSON.

## Testing
The included pytest suite checks allocation, deletion, bitmap consistency, persistence, permission checks, record access and input validation. Run the tests and include the actual terminal output in the final submission evidence.

## Limitations and future enhancements
The GUI is an educational prototype. Future work can add richer directory navigation, a complete explicit linked-block pointer table, per-directory access-control lists, expanded report export, and automated end-to-end tests for WSL integration.

## Conclusion
PyFileSystem provides an interactive demonstration of fundamental operating-system file-system concepts while maintaining separation between real Linux operations and virtual storage simulation.
