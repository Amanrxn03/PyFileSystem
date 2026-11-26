# Demonstration checklist

1. Start the GUI with `python main.py`.
2. Show Dashboard and explain virtual capacity versus real laboratory storage.
3. Open Virtual File Manager and create a sample file.
4. Demonstrate contiguous allocation and inspect the bitmap.
5. Create linked and indexed files and compare occupied blocks.
6. Delete one virtual file and show free blocks increase.
7. Open Permissions and demonstrate owner read allowed / others read denied.
8. Explain directory tree and access methods (sequential/direct).
9. If WSL is configured, create `demo.txt` in Actual Linux Files, read it, inspect metadata, change to 640, and delete it.
10. Run `python -m pytest -q` and capture the test results.
11. Restore safe permissions and ensure no test files remain in `lab_test`.
