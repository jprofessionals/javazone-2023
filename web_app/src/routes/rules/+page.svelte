<script lang="ts">
	import Img from '$lib/images/game-board-1.png'
</script>

<!-- <img src={Img} alt="dog" width="200" /> -->

<div class="w-full flex justify-center py-10 pb-20 text-black">
	<section class="prose parch p-4 rounded-lg mx-2 z-10">
		<h1 class="pixel-font">Game Rules</h1>
		<p>Welcome to our Microbit and Bitbot game! Here are the rules to get you started:</p>

		<h2 class="pixel-font">Objective</h2>
		<p>
			The goal of the game is to drive the Bitbot car around the field and gather as many points as
			possible in three rounds.
		</p>

		<h2 class="pixel-font">How to Play</h2>
		<ol class="list-disc marker:text-black">
			<li>Register in the app on our client machine.</li>
			<li>You will get three rounds to play.</li>
			<li>
				When you are ready, draw 7 random cards. Each card represents a direction:
				<div class="flex gap-2 flex-wrap">
					<div class="flex items-center gap-2">
						<img
							alt=""
							class="w-20 rotate-90"
							src="https://render.fineartamerica.com/images/rendered/medium/greeting-card/images/artworkimages/medium/2/illustration-of-hand-pointing-left-csa-images.jpg"
						/>
						Forward
					</div>
					<div class="flex items-center gap-2">
						<img
							alt=""
							class="w-20"
							src="https://render.fineartamerica.com/images/rendered/medium/greeting-card/images/artworkimages/medium/2/illustration-of-hand-pointing-left-csa-images.jpg"
						/>
						Left
					</div>
					<div class="flex items-center gap-2">
						<img
							alt=""
							class="w-20 rotate-180"
							src="https://render.fineartamerica.com/images/rendered/medium/greeting-card/images/artworkimages/medium/2/illustration-of-hand-pointing-left-csa-images.jpg"
						/>
						Left
					</div>
					<div class="flex items-center gap-2">
						<img
							alt=""
							class="w-20 -rotate-90"
							src="https://render.fineartamerica.com/images/rendered/medium/greeting-card/images/artworkimages/medium/2/illustration-of-hand-pointing-left-csa-images.jpg"
						/>
						U-turn
					</div>
					<div class="flex items-center gap-2">
						<div>
							<img
								alt=""
								class="w-20 rotate-90"
								src="https://render.fineartamerica.com/images/rendered/medium/greeting-card/images/artworkimages/medium/2/illustration-of-hand-pointing-left-csa-images.jpg"
							/>
							<img
								alt=""
								class="w-20 rotate-90 -mt-10"
								src="https://render.fineartamerica.com/images/rendered/medium/greeting-card/images/artworkimages/medium/2/illustration-of-hand-pointing-left-csa-images.jpg"
							/>
						</div>
						Double-forward [rare]
					</div>
				</div>
			</li>
			<li>Place the cards on the board in the order you want the car to move.</li>
			<li>
				The car will move from the starting intersection to the next intersection based on the
				direction of the cards.
			</li>
		</ol>

		<h2 class="pixel-font">Scoring</h2>
		<p>
			At each intersection, the player will either get positive or negative points. In the middle of
			the board, surrounded by negative points, there is a 6 pointer that could significantly
			increase your final score.
		</p>

		<h2 class="pixel-font">Game Board</h2>
		<div>
			<p>
				The game board is a rectangular board with black lines painted over that form intersections
				or crosses at each place a line crosses. These are the places where points are stored, and
				the car can drive to and fro.
			</p>
			<img src={Img} alt="dog" class="w-full" />
		</div>

		<h2 class="pixel-font">Winning</h2>
		<p>The player with the highest score at the end of the three rounds is the winner.</p>

		<h2 class="pixel-font">Good Luck!</h2>
		<p>Now that you know the rules, you are ready to play. Good luck!</p>
	</section>
</div>
