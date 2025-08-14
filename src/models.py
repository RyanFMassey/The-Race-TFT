class Summoner:
    def __init__(self, puuid, name, tag, tier, rank, lp, wins, losses, position, lp_delta, position_delta):
        self.rank = rank
        self.tier = tier
        self.lp = lp
        self.lp_delta = lp_delta
        self.position = position
        self.position_delta = position_delta

        self.wins = wins
        self.losses = losses
        self.games = wins + losses
        self.win_rate = f"{round(wins / self.games * 100, 1)}%"

        self.name = name
        self.tagline = tag
        self.puuid = puuid

    def to_dict(self):
        return {
            "puuid": self.puuid,
            "name": self.name,
            "tagline": self.tagline,
            "tier": self.tier,
            "rank": self.rank,
            "lp": self.lp,
            "lp_delta": self.lp_delta,
            "position": self.position,
            "position_delta": self.position_delta,
            "wins": self.wins,
            "losses": self.losses,
            "games": self.games,
            "win_rate": self.win_rate
        }

    @classmethod
    def from_dict(cls, data):
        return cls(
            puuid=data["puuid"],
            name=data["name"],
            tag=data["tagline"],
            tier=data["tier"],
            rank=data["rank"],
            lp=data["lp"],
            wins=data["wins"],
            losses=data["losses"],
            position=data["position"],
            lp_delta=data["lp_delta"],
            position_delta=data["position_delta"]
        )


class Rank:
    tierOrder = {
        'IRON': 1,
        'BRONZE': 2,
        'SILVER': 3,
        'GOLD': 4,
        'PLATINUM': 5,
        'EMERALD': 6,
        'DIAMOND': 7,
        'MASTER': 8,
        'GRANDMASTER': 9,
        'CHALLENGER': 10
    }

    rankOrder = {'IV': 1, 'III': 2, 'II': 3, 'I': 4}

    iconPath = {
        'IRON': 'Imgs/Ranks/Iron.png',
        'BRONZE': 'Imgs/Ranks/Bronze.png',
        'SILVER': 'Imgs/Ranks/Silver.png',
        'GOLD': 'Imgs/Ranks/Gold.png',
        'PLATINUM': 'Imgs/Ranks/Platinum.png',
        'EMERALD': 'Imgs/Ranks/Emerald.png',
        'DIAMOND': 'Imgs/Ranks/Diamond.png',
        'MASTER': 'Imgs/Ranks/Master.png',
        'GRANDMASTER': 'Imgs/Ranks/Grandmaster.png',
        'CHALLENGER': 'Imgs/Ranks/Challenger.png'
    }

    def rank_to_number(rank):
        if isinstance(rank, int):
            return str(f"#{rank}")

        rank_map = {'I': '1', 'II': '2', 'III': '3', 'IV': '4'}
        if rank in rank_map:
            return rank_map[rank]
        else:
            return None

    def calculate_score(tier, rank, lp):
        tier_points = (Rank.tierOrder[tier] - 1) * 400
        rank_points = (Rank.rankOrder[rank] - 1) * 100

        if tier == "MASTER":
            tier_points -= 300
        if tier == "GRANDMASTER":
            tier_points -= 700
        if tier == "CHALLENGER":
            tier_points -= 1100

        total = tier_points + rank_points + lp
        return total


class Player:
    def __init__(self, puuid, level, placement, traits):
        self.puuid = puuid
        self.level = level
        self.placement = placement
        self.traits = traits

    def __repr__(self):
        return f"Player(puuid={self.puuid}, level={self.level}, placement={self.placement}, traits={self.traits})"

    def to_dict(self):
        return {"puuid": self.puuid, "level": self.level, "placement": self.placement, "traits": [trait.to_dict() for trait in self.traits]}

    @classmethod
    def from_dict(cls, data):
        return cls(
            puuid=data["puuid"],
            level=data["level"],
            placement=data["placement"],
            traits=[Trait.from_dict(trait) for trait in data["traits"]]
        )


class Match:
    def __init__(self, match_id, players):
        self.match_id = match_id
        self.players = players  # players is a list of Player objects

    def __repr__(self):
        return f"Match(match_id={self.match_id}, players={self.players})"

    def to_dict(self):
        return {
            "match_id": self.match_id,
            "players": [player.to_dict() for player in self.players]  # Convert players to dictionaries
        }

    @classmethod
    def from_dict(cls, data):
        return cls(
            match_id=data["match_id"],
            players=[Player.from_dict(player) for player in data["players"]]
        )


class Trait:
    def __init__(self, trait, num_units):
        self.trait = trait
        self.num_units = num_units

    def __repr__(self):
        return f"Match(trait={self.trait}, num_units={self.num_units})"

    def to_dict(self):
        return {
            "trait": self.trait,
            "num_units": self.num_units
        }

    @classmethod
    def from_dict(cls, data):
        return cls(
            trait=data["trait"],
            num_units=data["num_units"]
        )
