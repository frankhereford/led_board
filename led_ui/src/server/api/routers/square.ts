import { z } from "zod";
var fontkit = require('fontkit');
import emoji from 'node-emoji';
import { PNG } from 'pngjs';

import { createTRPCRouter, publicProcedure } from "~/server/api/trpc";

import { createClient } from "redis";

const client = createClient({
  url: 'redis://localhost'
});

client.on('error', (err) => console.log('Redis Client Error', err));

await client.connect();

function parsePNG(buffer: Buffer): number[][][] {
  const png = PNG.sync.read(buffer);
  const { width, height, data } = png;
  const pixels: number[][][] = [];

  for (let y = 0; y < height; y++) {
    const row: number[][] = [];
    for (let x = 0; x < width; x++) {
      const idx = (width * y + x) << 2;
      row.push([data[idx]!, data[idx + 1]!, data[idx + 2]!]);
    }
    pixels.push(row);
  }

  return pixels;
}

export const squareRouter = createTRPCRouter({
  setColor: publicProcedure
    .input(z.object({
      x: z.number().int(),
      y: z.number().int(),
      color: z.array(z.number().int())
    }))
    .mutation(async ({ input }) => {
      const x = input.x
      const y = input.y
      console.log(input)

      await client.multi()
        .del(`display:${x}:${y}`)
        .rPush(`display:${x}:${y}`, input.color[0]?.toString()!)
        .rPush(`display:${x}:${y}`, input.color[1]?.toString()!)
        .rPush(`display:${x}:${y}`, input.color[2]?.toString()!)
        .publish('update', JSON.stringify({ x: x, y: y, color: input.color }))
        .exec();

      return ;
    }),

  getColor: publicProcedure
    .input(z.object({
      x: z.number().int(),
      y: z.number().int(),
    }))
    .query(async ({ input }) => {
      const x = input.x;
      const y = input.y;

      const color = await client.lRange(`display:${x}:${y}`, 0, -1);

      return color.map(value => parseInt(value, 10));
    }),

  getBoard: publicProcedure
    .query(async () => {
      const board = [];
      for (let y = 0; y < 24; y++) {
        const row = [];
        for (let x = 0; x < 24; x++) {
          const color = await client.lRange(`display:${x}:${y}`, 0, -1);
          row.push({
            color: color.map(value => parseInt(value, 10)),
            timestamp: Date.now()
          });
        }
        board.push(row);
      }
      return board;
    }),

  clearBoard: publicProcedure
    .mutation(async () => {
      const multi = client.multi();
      for (let y = 0; y < 24; y++) {
        for (let x = 0; x < 24; x++) {
          multi.del(`display:${x}:${y}`)
            .rPush(`display:${x}:${y}`, '0')
            .rPush(`display:${x}:${y}`, '0')
            .rPush(`display:${x}:${y}`, '0');
        }
      }
      await multi.publish('update', JSON.stringify({ clear: true })).exec();
    }),

  setEmoji: publicProcedure
    .input(z.object({emoji: z.string()}))
    .mutation(async () => {
      
      const font = fontkit.openSync('/home/frank/development/lightboard/led_ui/src/server/api/routers/apple-color-emoji.ttc').fonts[0]
      //console.log(font)
      const run = font.layout('️🐈‍⬛');
      const glyph = run.glyphs[0].getImageForSize(24);
      console.log(glyph)

      const pixels = parsePNG(glyph.data);
      console.log(pixels)

      const multi = client.multi();
      for (let y = 0; y < 24; y++) {
        for (let x = 0; x < 24; x++) {
          multi.del(`display:${x}:${y}`)
            .rPush(`display:${x}:${y}`, pixels[24 - y]![x]![0]!.toString())
            .rPush(`display:${x}:${y}`, pixels[24 - y]![x]![1]!.toString())
            .rPush(`display:${x}:${y}`, pixels[24 - y]![x]![2]!.toString());
        }
      }
      await multi.publish('update', JSON.stringify({ clear: true })).exec();
    }),


});
