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


def draw_position_square(draw, x, y, position, font):
    """
    Draws a 100x100 rounded square with a number inside.
    Color rules:
    - position == 1 → green
    - 2-4 → blue
    - 5-8 → white
    - else → grey
    """


    position_colors = {
        1: (17, 178, 136),
        2: (32, 122, 199),
        3: (32, 122, 199),
        4: (32, 122, 199),
        5: (207, 209, 215),
        6: (207, 209, 215),
        7: (207, 209, 215),
        8: (178, 24, 43)
    }

    square_color = position_colors.get(position)
    draw.rounded_rectangle((x, y, x + 100, y + 100),radius=20,fill=square_color)

    # Prepare text
    text = str(position)
    text_bbox = font.getbbox(text)
    text_width = text_bbox[2] - text_bbox[0]
    text_height = text_bbox[3] - text_bbox[1]

    # Center text in square
    text_x = x + 50 - text_width // 2
    text_y = y + 35 - text_height // 2

    # Text color rules
    if square_color == (207, 209, 215):  # gray
        text_color = (102, 106, 122)
    else:
        text_color = (255, 255, 255)

    # Draw text
    draw.text((text_x, text_y), text, fill=text_color, font=font)



def generate_image(old_summoners, summoners):
    # Calculate the size of the canvas based on the number of summoners
    canvas_width = 1920
    canvas_height = (140 * len(summoners) - 20 + 100)

    # Create image of rank list on top of background
    canvas = Image.new('RGBA', (canvas_width, canvas_height), (255, 255, 255, 0))
    draw = ImageDraw.Draw(canvas)

    # Load tier icons
    icons = {
        tier: Image.open(Rank.iconPath[tier]).resize((80, 80), resample=Image.BICUBIC)
        for tier in Rank.iconPath
    }

    hotStreakIcon = Image.open('Imgs/Fire emoji.png').resize((30, 30), resample=Image.BICUBIC)
    coldStreakIcon = Image.open('Imgs/Skull emoji.png').resize((30, 30), resample=Image.BICUBIC)

    crown_holder = min(summoners,key=lambda s: sum(s.recent_placements[:10]) if s.recent_placements else float('inf'))

    # Define box parameters
    box_width = 1920
    box_height = 120
    border_radius = 60

    # Define the new box colors
    first_place_color = (212, 175, 55)  # gold
    second_place_color = (192, 192, 192)  # silver
    third_place_color = (183, 119, 41)  # bronze

    # Write summoners info and tier icons to image
    font_title = ImageFont.truetype("ARIAL.TTF", 120)
    font_leaderboard_rank = ImageFont.truetype("ARIAL.TTF", 70)
    font_average_placement = ImageFont.truetype("ARIAL.TTF", 50)
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
        draw.ellipse((x + 1810, y + 10, x + 1910, y + 110), fill=circleColor)

        # Draw tier icon
        tierIcon = icons[summoner.tier]
        canvas.paste(tierIcon, (x + 135, y + 20), tierIcon)

        # Draw crown
        if summoner.puuid == crown_holder.puuid:
            print("Drawing crown for summoner:", summoner.name)
            crown = Image.open(f"Imgs/crown.png")
            canvas.paste(crown, (x + 157, y + 15), crown)

        # Draw Delta LP
        if old_summoner is not None:
            old_rank_score = Rank.calculate_score(old_summoner.tier, old_summoner.rank, old_summoner.lp)
            new_rank_score = Rank.calculate_score(summoner.tier, summoner.rank, summoner.lp)
            if old_rank_score != new_rank_score:
                draw.ellipse((x + 600, y + 10, x + 700, y + 110), fill=circleColor)
                delta_rank_score = new_rank_score - old_rank_score
                if delta_rank_score > 0:
                    textBbox = fontName.getbbox(f"+{delta_rank_score}")
                    textWidth = textBbox[2] - textBbox[0]
                    xCentered = x + 650 - textWidth // 2
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

        draw_text_centered(canvas, "SLASH COMMANDS: /add, /remove", 960, y + 10,
                           fontTier)

        # Draw recent placements
        draw_position_square(draw, x + 710, y - 130, summoner.recent_placements[0], font_leaderboard_rank)
        draw_position_square(draw, x + 820, y - 130, summoner.recent_placements[1], font_leaderboard_rank)
        draw_position_square(draw, x + 930, y - 130, summoner.recent_placements[2], font_leaderboard_rank)
        draw_position_square(draw, x + 1040, y - 130, summoner.recent_placements[3], font_leaderboard_rank)
        draw_position_square(draw, x + 1150, y - 130, summoner.recent_placements[4], font_leaderboard_rank)
        draw_position_square(draw, x + 1260, y - 130, summoner.recent_placements[5], font_leaderboard_rank)
        draw_position_square(draw, x + 1370, y - 130, summoner.recent_placements[6], font_leaderboard_rank)
        draw_position_square(draw, x + 1480, y - 130, summoner.recent_placements[7], font_leaderboard_rank)
        draw_position_square(draw, x + 1590, y - 130, summoner.recent_placements[8], font_leaderboard_rank)
        draw_position_square(draw, x + 1700, y - 130, summoner.recent_placements[9], font_leaderboard_rank)

        # Check last 3 placements for streaks
        recent_three = summoner.recent_placements[:3]

        # Win streak (all top 4)
        if len(recent_three) == 3 and all(p <= 4 for p in recent_three):
            print(summoner.name, "is on a win streak")
            taglineLength = draw.textlength(f"#{summoner.tagline}", font=fontTagline)
            canvas.paste(hotStreakIcon, (x + 245 + int(nameLength + taglineLength), y - 122), hotStreakIcon)
            print(x + 245 + int(nameLength + taglineLength), y + 50)

        # Loss streak (all bottom 4)
        elif len(recent_three) == 3 and all(p >= 5 for p in recent_three):
            print(summoner.name, "is on a loss streak")
            taglineLength = draw.textlength(f"#{summoner.tagline}", font=fontTagline)
            canvas.paste(coldStreakIcon, (x + 245 + int(nameLength + taglineLength), y - 122), coldStreakIcon)

        # Draw average placement
        draw_text_centered(canvas, f"{round(sum(summoner.recent_placements[:10]) / 10, 1)}", x + 1860, y - 85, font_average_placement)




    # Save image to file and show it
    canvas.save('Rank list.png')
