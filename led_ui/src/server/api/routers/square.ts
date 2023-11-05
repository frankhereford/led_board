import { z } from "zod";
import { observable } from '@trpc/server/observable';

import { createTRPCRouter, publicProcedure } from "~/server/api/trpc";

import { createClient } from "redis";

const client = createClient({
  url: 'redis://localhost'
});

client.on('error', (err) => console.log('Redis Client Error', err));

await client.connect();

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
});
