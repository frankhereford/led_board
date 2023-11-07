import { z } from "zod";
var fontkit = require('fontkit');
import { PNG } from 'pngjs';
import { createCanvas } from 'canvas';
const { CanvasEmoji } = require("canvas-emoji");
import emoji_lookup from '~/utils/emojis.json';
import { promises as fs } from 'fs';
import * as path from 'path';
import sharp from 'sharp';




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

function findEmojiEntry(emoji: string) {
  const emojis = emoji_lookup["emojis"] 
  const entry = (emojis.find(entry => entry.emoji === emoji))
  return entry
}

function createSlugFromEmojiObject(obj: { name: string }): string {
  return obj.name.toLowerCase().replace(/:|\s/g, '-').replace(/[^a-z0-9-]/g, '');
}

function formatUnicode(data: { emoji: string; name: string; shortname: string; unicode: string; html: string; category: string; order: string }): string {
  return data.unicode.toLowerCase().replace(/\s/g, '-');
}

async function findEmojiFile(unicodeString: string, directoryPath: string): Promise<string | null> {
  try {
    const files = await fs.readdir(directoryPath);
    const foundFile = files.find(file => file.includes(unicodeString));
    return foundFile ? path.join(directoryPath, foundFile) : null;
  } catch (error) {
    console.error('An error occurred:', error);
    return null;
  }
}

async function resizeImage(filePath: string): Promise<Buffer> {
  try {
    const buffer: Buffer = await sharp(filePath)
      .resize(24, 24)
      .toFormat('png')
      .toBuffer();
    return buffer;
  } catch (err) {
    console.error('Error processing image:', err);
    throw err;
  }
}

const getPixelData = async (buffer: Buffer): Promise<number[][]> => {
  const { data, info } = await sharp(buffer)
    .raw()
    .ensureAlpha()
    .toBuffer({ resolveWithObject: true });

  const pixels: number[][] = [];

  for (let i = 0; i < data.length; i += info.channels) {
    // Assuming the image is in RGBA format
    const r = data[i];
    const g = data[i + 1];
    const b = data[i + 2];
    // You can add alpha if you need it, just uncomment
    // const a = data[i + 3];

    pixels.push([r, g, b]); // or push [r, g, b, a] if you included alpha
  }

  return pixels;
};


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
    .mutation(async ({ input }) => {
      
      const entry = findEmojiEntry(input.emoji)
      const code = formatUnicode(entry)
      const directoryPath = '/var/lib/emoji-images';
      const filePath = await findEmojiFile(code, directoryPath);
      const imageBuffer = await resizeImage(filePath!);
      const pixels_list = await getPixelData(imageBuffer);
      const pixels = Array.from({ length: 24 }, (_, i) => pixels_list.slice(i * 24, i * 24 + 24));

      const threshold = 20
      const multi = client.multi();
      for (let y = 0; y < 24; y++) {
        for (let x = 0; x < 24; x++) {
          if (pixels[y][x][0] < threshold && pixels[y][x][1] < threshold && pixels[y][x][2] < threshold) {
            pixels[y][x] = [0, 0, 0];
          }

          multi.del(`display:${x}:${y}`)
            .rPush(`display:${x}:${y}`, pixels[y][x][0].toString())
            .rPush(`display:${x}:${y}`, pixels[y][x][1].toString())
            .rPush(`display:${x}:${y}`, pixels[y][x][2].toString())
        }
      }
      await multi.publish('update', JSON.stringify({ clear: true })).exec();

    }),


});
