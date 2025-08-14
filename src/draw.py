from PIL import ImageFont
from PIL import Image, ImageDraw
from models import Rank


def draw_text_centered(canvas, text, x, y, font, colour=(255, 255, 255)):
    # Get the size of the text using the provided font
    draw = ImageDraw.Draw(canvas)
    textBbox = draw.textbbox((x, y), text, font=font)

    # Calculate the x and y positions to center the text
    centerX = x - (textBbox[2] - textBbox[0]) / 2
    centerY = y - (textBbox[3] - textBbox[1]) / 2

    # Draw the text at the center position with the specified opacity
    draw.text((centerX, centerY), text, colour, font=font)


def generate_image(old_summoners, summoners):
    # Calculate the size of the canvas based on the number of summoners
    canvas_width = 1820
    canvas_height = (140 * len(summoners) - 20 + 100)

    # Create image of rank list on top of background
    canvas = Image.new('RGBA', (canvas_width, canvas_height), (255, 255, 255, 0))
    draw = ImageDraw.Draw(canvas)

    # Load tier icons
    icons = {
        tier: Image.open(Rank.iconPath[tier]).resize((80, 80), resample=Image.BICUBIC)
        for tier in Rank.iconPath
    }

    # Define box parameters
    box_width = 1820
    box_height = 120
    border_radius = 60

    # Define the new box colors
    first_place_color = (212, 175, 55)  # gold
    second_place_color = (192, 192, 192)  # silver
    third_place_color = (183, 119, 41)  # bronze

    # Write summoners info and tier icons to image
    font_title = ImageFont.truetype("ARIAL.TTF", 120)
    font_leaderboard_rank = ImageFont.truetype("ARIAL.TTF", 70)
    fontName = ImageFont.truetype("ARIAL.TTF", 40)
    fontTagline = ImageFont.truetype("ARIAL.TTF", 16)
    fontTier = ImageFont.truetype("ARIAL.TTF", 32)
    fontLp = ImageFont.truetype("ARIAL.TTF", 24)

    y = 0
    for i, summoner in enumerate(summoners):
        old_summoner = next(
            (s for s in old_summoners if s.name + "#" + s.tagline == summoner.name + "#" + summoner.tagline), None)
        # Determine the box color based on summoner rank
        boxColor = (49, 49, 60, 255)  # default box color

        if i == 0:
            boxColor = first_place_color
        elif i == 1:
            boxColor = second_place_color
        elif i == 2:
            boxColor = third_place_color

        # Draw box background
        x = 0
        boxPos = (x, y, x + box_width, y + box_height)
        circleColor = (40, 40, 48, 255)
        draw.rounded_rectangle(boxPos, border_radius, boxColor, None)
        draw.ellipse((x + 120, y + 10, x + 230, y + 110), fill=circleColor)
        draw.ellipse((x + 10, y + 10, x + 110, y + 110), fill=circleColor)

        # Draw tier icon
        tierIcon = icons[summoner.tier]
        canvas.paste(tierIcon, (x + 135, y + 20), tierIcon)

        # Draw Delta LP
        if old_summoner is not None:
            old_rank_score = Rank.calculate_score(old_summoner.tier, old_summoner.rank, old_summoner.lp)
            new_rank_score = Rank.calculate_score(summoner.tier, summoner.rank, summoner.lp)
            if old_rank_score != new_rank_score:
                draw.ellipse((x + 610, y + 10, x + 710, y + 110), fill=circleColor)
                delta_rank_score = new_rank_score - old_rank_score
                if delta_rank_score > 0:
                    textBbox = fontName.getbbox(f"+{delta_rank_score}")
                    textWidth = textBbox[2] - textBbox[0]
                    xCentered = x + 660 - textWidth // 2
                    draw.text((xCentered, y + 40), f"+{delta_rank_score}", (50, 200, 50), font=fontName)
                else:
                    textBbox = fontName.getbbox(f"{delta_rank_score}")
                    textWidth = textBbox[2] - textBbox[0]
                    xCentered = x + 660 - textWidth // 2
                    draw.text((xCentered, y + 40), f"{delta_rank_score}", (200, 50, 50), font=fontName)

        if (old_summoner is not None) and (old_summoner.position != summoner.position):
            draw.ellipse((x + 490, y + 10, x + 590, y + 110), fill=circleColor)
            delta_position = summoner.position - old_summoner.position
            if delta_position < 0:
                triangleCoordsUp = [(x + 530, y + 70), (x + 540, y + 50), (x + 550, y + 70)]
                draw.polygon(triangleCoordsUp, fill=(50, 200, 50), outline=(0, 0, 0))
            else:
                triangleCoordsDown = [(x + 530, y + 50), (x + 540, y + 70), (x + 550, y + 50)]
                draw.polygon(triangleCoordsDown, fill=(200, 50, 50), outline=(0, 0, 0))

        # Calculate the length of the summoner.name
        nameLength = draw.textlength(summoner.name, font=fontName)

        # Draw summoner name with fontName
        draw.text((x + 240, y + 10), summoner.name, (255, 255, 255), font=fontName)

        # Draw summoner tagline with fontLp after the summoner.name
        draw.text((x + 240 + nameLength + 5, y + 31), f"#{summoner.tagline}", (255, 255, 255), font=fontTagline)

        # Draw summoner tier and rank
        draw.text((x + 240, y + 54), f"{summoner.tier} {Rank.rank_to_number(summoner.rank)}", (255, 255, 255),
                  font=fontTier)
        draw.text((x + 240, y + 90),
                  f"{summoner.lp} LP {summoner.wins}/{summoner.losses} {summoner.win_rate}",
                  (255, 255, 255), font=fontLp)
        draw_text_centered(canvas, f"{summoner.position}", x + 60, y + 50, font_leaderboard_rank)

        # Increment y position for next summoners
        y += box_height + 20

        draw_text_centered(canvas, "SLASH COMMANDS: /add, /remove", 910, y + 10,
                           fontTier)

    # Save image to file and show it
    canvas.save('Rank list.png')
