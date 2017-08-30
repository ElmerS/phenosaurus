# Public Phenosaurus version running

30th August 2017
- Updated the CCS of the main application. Switched from custom CSS to Bootstrap v3.
- Fixed bug that caused requests to draw a geneplot of a gene that does exist in the database but was never a hit in the screen to result in a 400 (bad request) error
- Made several error messages more readable
- Fix bug where extended genenames (such as AGAP9@chr10+) did not result in a valid link to UCSC
