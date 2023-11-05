import { z } from "zod";
import { observable } from '@trpc/server/observable';
//import { WebSocketServer } from 'ws';

import { createTRPCRouter, publicProcedure } from "~/server/api/trpc";

import { createClient } from "redis";

const client = createClient({
  // your redis configuration
  url: 'redis://localhost'
});

client.on('error', (err) => console.log('Redis Client Error', err));

await client.connect();

export const squareRouter = createTRPCRouter({
  color: publicProcedure
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
        .exec();

      return ;
    }),

});
