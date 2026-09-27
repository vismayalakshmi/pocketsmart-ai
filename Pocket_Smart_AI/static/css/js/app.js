function renderResult(data) {
    const box = document.getElementById("result");

    if (!box) {
        return;
    }

    box.innerHTML = "";

    const pre = document.createElement("pre");

    pre.textContent =
        JSON.stringify(
            data,
            null,
            2
        );

    box.appendChild(pre);
}


async function postJSON(
    url,
    payload
) {
    const response = await fetch(
        url,
        {
            method: "POST",

            headers: {
                "Content-Type":
                    "application/json"
            },

            body: JSON.stringify(
                payload
            )
        }
    );

    const data =
        await response.json();

    if (!response.ok) {
        throw new Error(
            data.detail ||
            data.error ||
            "Request failed."
        );
    }

    return data;
}


/* -----------------------
   HOME PLANNER
----------------------- */

const homeForm =
    document.getElementById(
        "homeForm"
    );


if (homeForm) {

    homeForm.addEventListener(
        "submit",
        async function (event) {

            event.preventDefault();

            try {

                const rooms =
                    document
                        .getElementById(
                            "rooms"
                        )
                        .value
                        .split(",")
                        .map(
                            function (room) {
                                return room.trim();
                            }
                        )
                        .filter(
                            Boolean
                        );


                const data =
                    await postJSON(
                        "/api/home-planner",
                        {
                            budget:
                                Number(
                                    document
                                        .getElementById(
                                            "budget"
                                        )
                                        .value
                                ),

                            lights:
                                Number(
                                    document
                                        .getElementById(
                                            "lights"
                                        )
                                        .value
                                ),

                            fans:
                                Number(
                                    document
                                        .getElementById(
                                            "fans"
                                        )
                                        .value
                                ),

                            furniture:
                                Number(
                                    document
                                        .getElementById(
                                            "furniture"
                                        )
                                        .value
                                ),

                            rooms: rooms,

                            preferences:
                                document
                                    .getElementById(
                                        "preferences"
                                    )
                                    .value
                        }
                    );


                renderResult(data);

            } catch (error) {

                renderResult({
                    error: error.message
                });

            }

        }
    );
}


/* -----------------------
   PARTY PLANNER
----------------------- */

const partyForm =
    document.getElementById(
        "partyForm"
    );


if (partyForm) {

    partyForm.addEventListener(
        "submit",
        async function (event) {

            event.preventDefault();

            try {

                const data =
                    await postJSON(
                        "/api/party-planner",
                        {
                            budget:
                                Number(
                                    document
                                        .getElementById(
                                            "budget"
                                        )
                                        .value
                                ),

                            guests:
                                Number(
                                    document
                                        .getElementById(
                                            "guests"
                                        )
                                        .value
                                ),

                            event_type:
                                document
                                    .getElementById(
                                        "event_type"
                                    )
                                    .value,

                            food_preference:
                                document
                                    .getElementById(
                                        "food_preference"
                                    )
                                    .value,

                            venue_preference:
                                document
                                    .getElementById(
                                        "venue_preference"
                                    )
                                    .value,

                            preferences:
                                document
                                    .getElementById(
                                        "preferences"
                                    )
                                    .value
                        }
                    );


                renderResult(data);

            } catch (error) {

                renderResult({
                    error: error.message
                });

            }

        }
    );
}


/* -----------------------
   JEWELRY PLANNER
----------------------- */

const jewelryForm =
    document.getElementById(
        "jewelryForm"
    );


if (jewelryForm) {

    jewelryForm.addEventListener(
        "submit",
        async function (event) {

            event.preventDefault();

            const box =
                document.getElementById(
                    "result"
                );

            if (box) {
                box.textContent =
                    "Analyzing outfit...";
            }


            try {

                const response =
                    await fetch(
                        "/api/jewelry-planner",
                        {
                            method: "POST",
                            body:
                                new FormData(
                                    jewelryForm
                                )
                        }
                    );


                const data =
                    await response.json();


                if (!response.ok) {

                    throw new Error(
                        data.detail ||
                        "Request failed."
                    );

                }


                renderResult(data);

            } catch (error) {

                renderResult({
                    error: error.message
                });

            }

        }
    );
}