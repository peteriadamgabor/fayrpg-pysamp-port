------- PLAYER PLARAMETER TRIGGER -------
CREATE OR REPLACE FUNCTION create_player_variable()
    RETURNS TRIGGER AS
$$
BEGIN
    INSERT INTO public.player_parameters (player_id)
    VALUES (NEW.id);
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DO $$
    BEGIN
        IF EXISTS (SELECT 1 FROM pg_trigger WHERE tgname = 'after_player_insert') THEN
            RAISE NOTICE 'DROP TRIGGER after_player_insert ON players;';
            DROP TRIGGER after_player_insert ON players;
        END IF;

        RAISE NOTICE 'CREATE TRIGGER after_player_insert;';

        CREATE TRIGGER after_player_insert
            AFTER INSERT
            ON players  -- Explicitly specify the schema (if needed)
            FOR EACH ROW
        EXECUTE FUNCTION create_player_variable();
    END;
$$;
------- PLAYER PLARAMETER TRIGGER -------
