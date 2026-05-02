import asyncio

from google.apps import meet_v2


async def main():
    print("creating meet...")

    # Create a client
    client = meet_v2.SpacesServiceAsyncClient()

    # Initialize request argument(s)
    request = meet_v2.CreateSpaceRequest()

    # Make the request
    response = await client.create_space(request=request)

    # Handle the response
    print(response)


if __name__ == "__main__":
    asyncio.run(main())
