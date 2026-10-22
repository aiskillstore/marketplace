// Extractor registry. Add one by exporting {name, kind, test(src, file), symbols?(src), routes?(src)} and
// listing it here. symbols() returns named shapes; routes() returns http/rpc/topic entries that point at them.
import zod from './zod.mjs';
import joi from './joi.mjs';
import classValidator from './class-validator.mjs';
import tsTypes from './ts-types.mjs';
import express from './express.mjs';
import nest from './nest.mjs';
import topicProducer from './topic-producer.mjs';
import openapi from './openapi.mjs';
import protobuf from './protobuf.mjs';
export const EXTRACTORS = [zod, joi, classValidator, tsTypes, express, nest, topicProducer, openapi, protobuf];
export const EXTRACTOR_VERSION = 'transit-contracts-2';
