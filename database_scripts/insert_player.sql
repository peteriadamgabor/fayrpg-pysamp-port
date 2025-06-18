CREATE EXTENSION IF NOT EXISTS pgcrypto;

CREATE OR REPLACE FUNCTION insert_player(
    p_username TEXT,
    p_password TEXT,
    p_sex INT,
    p_birth_day DATE
) RETURNS VOID AS $$
DECLARE
  hashed_password TEXT;
BEGIN
  IF p_username IS NULL OR p_username = '' OR p_password IS NULL OR p_password = '' THEN
      RAISE EXCEPTION 'Username and password cannot be empty.' USING ERRCODE = 'invalid_parameter_value';
  END IF;

  hashed_password := crypt(p_password, gen_salt('bf', 16));

  INSERT INTO public.players(name, password, sex, birthdate)
  VALUES (p_username, hashed_password, p_sex, p_birth_day);
END;
$$ LANGUAGE plpgsql SECURITY INVOKER;

CREATE OR REPLACE FUNCTION change_player_password(
    p_username TEXT,
    p_new_password TEXT
) RETURNS VOID AS $$
DECLARE
  hashed_password TEXT;
BEGIN
  IF p_username IS NULL OR p_username = '' OR p_new_password IS NULL OR p_new_password = '' THEN
      RAISE EXCEPTION 'Username and new password cannot be empty.' USING ERRCODE = 'invalid_parameter_value';
  END IF;

  hashed_password := crypt(p_new_password, gen_salt('bf', 16));

  UPDATE public.players
  SET password = hashed_password
  WHERE name = p_username;

  IF NOT FOUND THEN
    RAISE EXCEPTION 'Player username "%" not found.', p_username
      USING ERRCODE = 'no_data_found';
  END IF;

END;
$$ LANGUAGE plpgsql SECURITY INVOKER;

CREATE OR REPLACE FUNCTION verify_player_password(
    p_username TEXT,
    p_password_attempt TEXT
) RETURNS BOOLEAN AS $$
DECLARE
    stored_hash TEXT;
BEGIN

    IF p_username IS NULL OR p_username = '' OR p_password_attempt IS NULL OR p_password_attempt = '' THEN
        RETURN FALSE;
    END IF;

    SELECT password INTO stored_hash FROM public.players WHERE name = p_username;

    IF NOT FOUND THEN
        RETURN FALSE;
    END IF;

    RETURN stored_hash = crypt(p_password_attempt, stored_hash);
END;
$$ LANGUAGE plpgsql SECURITY INVOKER;
