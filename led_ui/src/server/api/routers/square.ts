import { z } from "zod";

import { createTRPCRouter, publicProcedure } from "~/server/api/trpc";

import { createClient } from "redis";
//import Redis from 'ioredis';

let post = {
  id: 1,
  name: "Hello World",
};

const client = createClient({
  // your redis configuration
  url: 'redis://localhost'
});

client.on('error', (err) => console.log('Redis Client Error', err));

await client.connect();

function generateTuples(n: number): Array<any> {
  // Your tuple generation logic here
  return [['value1', 'value2']]; // Example return value
}

export const squareRouter = createTRPCRouter({
  hello: publicProcedure
    .input(z.object({ text: z.string() }))
    .query(({ input }) => {
      return {
        greeting: `Hello ${input.text}`,
      };
    }),

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
      //const randomValues = generateTuples(1)[0]; // Ensure generateTuples is defined
      console.log(input.color)
      await client.multi()
        .del(`display:${x}:${y}`)
        .rPush(`display:${x}:${y}`, input.color[0]?.toString()!)
        .rPush(`display:${x}:${y}`, input.color[1]?.toString()!)
        .rPush(`display:${x}:${y}`, input.color[2]?.toString()!)
        .exec();

      //await client.disconnect();
      
      //const redisClient = await createClient({
        //url: 'redis://localhost'
      //}).connect();

      // simulate a slow db call
      //await new Promise((resolve) => setTimeout(resolve, 1000));

      //post = { id: post.id + 1, name: input.name };
      return post;
    }),

  getLatest: publicProcedure.query(() => {
    return post;
  }),
});
