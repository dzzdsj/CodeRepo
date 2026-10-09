import api from "./index"

export function getUsers() {
    return api.get("/api/users")
}