use network_libp2p::{CustomMessage, CustomMessageId};

use crate::codec::{Decoder, Encoder};
use crate::codec::serde::SerdeCodec;

pub type RequestId = u64;

lazy_static! {
    static ref CODEC: SerdeCodec<NetworkMessage> = SerdeCodec::new();
}

#[derive(Clone, Debug, Deserialize, Serialize)]
pub enum NetworkMessage {
	Blob(Vec<u8>),
}

impl CustomMessage for NetworkMessage {
	fn into_bytes(self) -> Vec<u8> {
		CODEC.encode(&self).unwrap()
	}

	fn from_bytes(bytes: &[u8]) -> Result<Self, ()> where Self: Sized {
		match CODEC.decode(bytes) {
			Ok(m) => match m {
				Some(m) => Ok(m),
				None => Err(()),
			},
			Err(_) => Err(())
		}
	}

	fn request_id(&self) -> CustomMessageId {
		match *self {
			_ => CustomMessageId::OneWay,
		}
	}
}
