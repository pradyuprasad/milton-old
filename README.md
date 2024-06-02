# EconDataGPT

The basic thesis:

- There is a lot of economic data in the world
- We still need a lot of skills to access it
  - knowing which dataset
  - how to access it
  - how to use the data correctly
  - random programming stuff

- We take over that. You focus on your writing. We focus on the technical part

How do we do this?

- local storage of data in GPT-readable format
- pick the right dataset(s)
- use those to answer the question and generate cool graphs
- send to user

What are the steps?

- Download the data
  - What data?
  - Singapore GDP and inflation data, I have already built a downloader for SGDataProject
  - Build MVP on that tomorrow.
  - What can I do in this that is better than SGDataProject??
    - Basic structure is the same as always
    - Have a lot of CSV files (do I need to?)
    - Make a very good dataset selector
    - Make a very good code writing agent
    - ???
    - Profit

Goal for tomorrow (3 June)

- Download data
  - From SingStat and FRED
    - All GDP data from SingStat?
    - write data downlader for SingStat data
    - use inspiration from old repo
    - one subseries, one CSV file. (Does this make sense? How to align with FRED?)
      - How to deal with sector levels?
      - main problem is model needs to realise the correct level of depth to go for each query
        - need to prompt it better.
  - think of way to ogranise data from FRED
- Write dataset annotator
- Upload data to object storage?
  - check options for object storage out
- Write dataset selector
- Write mockup in figma
- work your ass off!!
