from spotify import Spotify
import json
# import random
# import colorama

s = Spotify()

def main():
    with open("data.json", 'w', encoding="UTF-8") as f:
        json.dump(
            s.get_playlists_songs(), f, indent=4, ensure_ascii=False
        )

if __name__ == "__main__":
    main()

# colorama.initialise.init(autoreset=True)
# G = colorama.ansi.Fore.GREEN
# C = colorama.ansi.Fore.CYAN
# R = colorama.ansi.Fore.RED
# Y = colorama.ansi.Fore.YELLOW

# spotify = SP().spotify

# def get_playlists():
#     playlists = spotify.current_user_playlists()

#     for p in playlists["items"]:
#         p_name = p["name"]
#         p_id = p["id"]
#         p_snapshot_id = p["snapshot_id"]
#         p_len = p["tracks"]["total"]
        
#         print(Y+f"Playlist: {p_name}\n  snapshot: {p_snapshot_id}\n  total track count: {p_len}\n  playlist id: {p_id}")
#         answer = input(C+"Do you want to randomize playlist? (y): ").lower()
        
#         if answer == "y":
#             return p
        
#         print(R+"%s passed." % p_name)

#     tracks_uri = p["tracks"]["href"]
#     tracks_will_randomize = []
    
#     Offset = 0
#     while True:
#         songs = []
#         for track in spotify.playlist_items(p_id, limit=100, offset=Offset)["items"]:
#             t_id = track["track"]["id"]
#             t_name = track["track"]["name"]
#             songs.append(t_id)

#         tracks_will_randomize.extend(songs)
#         if not len(songs) == 100:
#             break
        
#         songs.clear()
#         Offset += 100
    
#     random.shuffle(tracks_will_randomize)
    
#     # FIXME this will be fixed (100 limit)
#     for i in range(0, len(tracks_will_randomize)+1, 100):
#         for x in tracks_will_randomize[0:100+i]:
#             spotify.playlist_reorder_items(
#                 playlist_id=p_id,
#                 range_length=100,
#                 insert_before=i,
#                 range_start=i
#             )
    
#     tracks_will_randomize.clear()
#     print(G+"%s successfully randomized." % p_name)
