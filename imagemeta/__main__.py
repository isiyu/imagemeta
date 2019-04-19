from .imageMetaLib import get_bucket_meta_json
from .imageMetaLib import get_image_meta_json

import argparse
import sys

def main():
    parser = argparse.ArgumentParser(
            description='Outputs exif_metadata of images on Google cloud'
                        '\n requires OAuth via a Google account')
    # The following argument(s) should be provided to run the example.
    parser.add_argument('--bucket', required=False,
                            help=('Get metadata for all files in given bucket'))
    parser.add_argument('--file', required=False,
                            help=('Get metadata given file including bucket'
                                   '\n ex. /my-bucket/image.jpg'
                                    ))
    parser.add_argument('--write', required=False,
                            help=('write meta data json to file '))

    args = parser.parse_args()
    if args.bucket and args.file:
        print("requires --bucket OR --file flag")
    if args.bucket == None and args.file == None:
        parser.print_usage()

    if args.bucket:
        get_bucket_meta_json( args.bucket, args.write )
    if args.file:
        get_image_meta_json( args.file, args.write )

if __name__ == '__main__':
    main()
