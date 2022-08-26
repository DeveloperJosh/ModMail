from discord import Embed
import discord

def error_embed(title: str, description: str) -> Embed:
    return Embed(
        title=title,
        description=description,
        color=discord.Color.red()
    )

def custom_embed_with_image(title: str, description: str, image: str) -> Embed:
    return Embed(
        title=title,
        description=description,
        color=discord.Color.blue(),
        image=image  # type: ignore
    )

def warning_embed(title: str, description: str) -> Embed:
    return Embed(
        title=title,
        description=description,
        color=0xffff00
    )


def success_embed(title: str, description: str) -> Embed:
    return Embed(
        title=title,
        description=description,
        color=discord.Color.green()
    )


def custom_embed(title: str, description: str) -> Embed:
    return Embed(
        title=title,
        description=description,
        color=discord.Color.blue()
    )