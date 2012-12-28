#!/usr/bin/python -tt
#---------------------------------------------------------------------
# Module Name:  exif_parser.py
#
# Description:  This module parses a JPEG file and returns the exif
#               data.
#
# Author:       Wesley Detweiler
#
# Date:         12-27-2012
#---------------------------------------------------------------------
import struct
import sys


#---------------------------------------------------------------------
# Function Name - read_app1()
#
# Desctiption - This function gets the location of app1 and gets the
#               byte order of the data.
#---------------------------------------------------------------------
def read_app1( data, app1_address ):
    ret_val = 0
    current_address = app1_address
    current_address += 2
    size_tuple = struct.unpack( '>H', data[current_address:current_address+2] )
    size = size_tuple[0] - 2
    current_address += 2
    exif_identifier = struct.unpack( '>L', data[current_address:current_address+4] )
    if exif_identifier == ( 0x45786966, ):
        current_address += 6
        base_offset = current_address
        byte_order = struct.unpack( '>H', data[current_address:current_address+2] )
        current_address += 4
        if byte_order == ( 0x4949, ):
            next_ifd = struct.unpack( '<L', data[current_address:current_address+4] )
        else:
            next_ifd = struct.unpack( '>L', data[current_address:current_address+4] )
        if next_ifd[0] != 0:
            current_address = base_offset + next_ifd[0]
            read_ifd( data, current_address, base_offset, byte_order)
        print next_ifd
        print hex( current_address )
    else:
        ret_val = -1
    
    return ret_val
#   read_app1()


#---------------------------------------------------------------------
# Function Name - read_ifd()
#
# Desctiption - This function finds the IFD field count and gets the
#               offsets
#---------------------------------------------------------------------
def read_ifd( data, address, base_offset, byte_order ):
    current_address = address
    if byte_order == ( 0x4949, ):
        field_count = struct.unpack( '<H', data[current_address:current_address+2] )
    else:
        field_count = struct.unpack( '>H', data[current_address:current_address+2] )
    current_address += 2
    i = 0
    
    print 'field count:'
    print field_count[0]
    while i < field_count[0]:
        read_field( data, current_address, base_offset, byte_order )
        current_address += 12
        i += 1
#   read_ifd()


#---------------------------------------------------------------------
# Function Name - read_field()
#
# Desctiption - This function parses the IFD fields.
#---------------------------------------------------------------------
def read_field( data, address, base_offset, byte_order):
    current_address = address
    n = 0
    print 'read_field called'
    if byte_order == ( 0x4949, ):
        tag_id = struct.unpack( '<H', data[current_address:current_address+2] )
    else:
        tag_id = struct.unpack( '>H', data[current_address:current_address+2] )
    print 'tag id:',
    print tag_id
    current_address += 2
    
    if byte_order == ( 0x4949, ):
        field_type = struct.unpack( '<H', data[current_address:current_address+2] )
    else:
        field_type = struct.unpack( '>H', data[current_address:current_address+2] )
    
    current_address += 2
    
    if byte_order == ( 0x4949, ):
        count = struct.unpack( '<L', data[current_address:current_address+4] )
    else:
        count = struct.unpack( '>L', data[current_address:current_address+4] )
    print 'count:',
    print count
    current_address += 4
    
    print 'field type:',
    print field_type
    # Byte length of field data
    if field_type[0] == 1:
        n = count[0] #1-byte x count
    elif field_type[0] == 2 or field_type == 7:
        n = count[0] #1-byte x count
    elif field_type[0] == 3:
        n = 2 * count[0] #2-bytes x count
    elif field_type[0] == 4 or field_type == 9:
        n = 4 * count[0] #4-bytes x count
    elif field_type[0] == 5 or field_type == 10:
        n = 8 * count[0] #2 x 4-bytes x count
    
    if byte_order == ( 0x4949, ):
        value = struct.unpack( '<L', data[current_address:current_address+4] )
    else:
        value = struct.unpack( '>L', data[current_address:current_address+4] )
    current_address += 4
    
    if n > 4:
        current_offset = current_address
        
        current_address = base_offset + value[0]
        
        num_str = str( n )
        amount = num_str + 'B'
        value =  struct.unpack( amount, data[current_address:(current_address+n)] )
        print 'value:',
        print value
        
        current_address = current_offset
#   read_field()


#---------------------------------------------------------------------
# Function Name - main()
#
# Desctiption - This is the main function for the module.
#---------------------------------------------------------------------
def main():
    file = open( sys.argv[1], 'rb' )
    data = file.read()
    marker = struct.unpack( '>H', data[0:2] )
    if marker != ( 0xffd8, ):
        print 'Not a JPEG image.'
        print 'Exiting'
    else:
        loop = 2
        marker = 0
        while loop < ( len( data ) - 1 ) and marker != ( 0xffd9, ):
            marker = struct.unpack( '>H', data[loop:loop+2] )
            size = struct.unpack( '>H', data[loop+2:loop+4] )
            if marker == ( 0xffe1, ):
                print 'app1 address: ' + hex( loop )
                app1_address = loop
                app1_return = read_app1( data, app1_address )
                if app1_return < 0:
                    print 'app1 read faild'
            loop += ( size[0] + 2 )
      

    print 'done'
#   main()

# This is the standard boilerplate that calls the main() function.
if __name__ == '__main__':
    main()
