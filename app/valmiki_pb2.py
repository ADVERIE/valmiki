# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# NO CHECKED-IN PROTOBUF GENCODE
# source: valmiki.proto
# Protobuf Python Version: 5.29.0
"""Generated protocol buffer code."""
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import runtime_version as _runtime_version
from google.protobuf import symbol_database as _symbol_database
from google.protobuf.internal import builder as _builder
_runtime_version.ValidateProtobufRuntimeVersion(
    _runtime_version.Domain.PUBLIC,
    5,
    29,
    0,
    '',
    'valmiki.proto'
)
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()




DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n\rvalmiki.proto\x12\x07valmiki\"$\n\x0ePredictRequest\x12\x12\n\nimage_data\x18\x01 \x01(\x0c\"H\n\x0fPredictResponse\x12\x11\n\tage_group\x18\x01 \x01(\t\x12\x0e\n\x06gender\x18\x02 \x01(\t\x12\x12\n\nconfidence\x18\x03 \x01(\x02\x32N\n\x0eValmikiService\x12<\n\x07Predict\x12\x17.valmiki.PredictRequest\x1a\x18.valmiki.PredictResponseB\x1cZ\x1agyandoot-svc/proto/valmikib\x06proto3')

_globals = globals()
_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, _globals)
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'valmiki_pb2', _globals)
if not _descriptor._USE_C_DESCRIPTORS:
  _globals['DESCRIPTOR']._loaded_options = None
  _globals['DESCRIPTOR']._serialized_options = b'Z\032gyandoot-svc/proto/valmiki'
  _globals['_PREDICTREQUEST']._serialized_start=26
  _globals['_PREDICTREQUEST']._serialized_end=62
  _globals['_PREDICTRESPONSE']._serialized_start=64
  _globals['_PREDICTRESPONSE']._serialized_end=136
  _globals['_VALMIKISERVICE']._serialized_start=138
  _globals['_VALMIKISERVICE']._serialized_end=216
# @@protoc_insertion_point(module_scope)
