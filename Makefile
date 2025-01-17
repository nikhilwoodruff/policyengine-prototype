run-api:
	cd api && LOCAL=true fastapi dev

run-app:
	cd app && LOCAL=true next dev

run-db:
	cd supabase && supabase start
