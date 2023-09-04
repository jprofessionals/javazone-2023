import { SECRET_KEY } from '$env/static/private'

export const validateCUDRequest = (secret: string | null) => secret === SECRET_KEY
