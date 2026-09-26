package com.meditracex.app.ui.components

import androidx.compose.foundation.BorderStroke
import androidx.compose.foundation.background
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material3.*
import androidx.compose.runtime.Composable
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.meditracex.app.data.model.DemandPredictionResponse
import com.meditracex.app.ui.theme.*

@Composable
fun PredictionResultCard(
    prediction: DemandPredictionResponse,
    modifier: Modifier = Modifier
) {
    Card(
        modifier = modifier.fillMaxWidth(),
        shape = RoundedCornerShape(16.dp),
        colors = CardDefaults.cardColors(containerColor = SurfaceLight),
        border = BorderStroke(1.dp, DividerColor),
        elevation = CardDefaults.cardElevation(defaultElevation = 2.dp)
    ) {
        Column(modifier = Modifier.padding(16.dp)) {
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceBetween,
                verticalAlignment = Alignment.CenterVertically
            ) {
                Column {
                    Text(
                        text = prediction.medicineName,
                        fontWeight = FontWeight.Bold,
                        fontSize = 16.sp,
                        color = TextPrimary
                    )
                    Text(
                        text = prediction.pharmacyName,
                        fontSize = 12.sp,
                        color = TextSecondary
                    )
                }

                StockoutRiskBadge(riskLevel = prediction.stockOutRisk)
            }

            Spacer(modifier = Modifier.height(14.dp))

            // Key Metrics Matrix
            Row(
                modifier = Modifier
                    .fillMaxWidth()
                    .clip(RoundedCornerShape(12.dp))
                    .background(SurfaceVariantLight)
                    .padding(12.dp),
                horizontalArrangement = Arrangement.SpaceAround
            ) {
                MetricColumn(title = "Current Stock", value = "${prediction.currentStock} units")
                MetricColumn(title = "Next-Day Pred", value = "${prediction.predictedNextDayDemand} units")
                MetricColumn(title = "7-Day Total", value = "${prediction.predicted7DayDemand} units")
            }

            Spacer(modifier = Modifier.height(12.dp))

            // Restock recommendation callout
            Surface(
                shape = RoundedCornerShape(10.dp),
                color = if (prediction.suggestedRestockQuantity > 0) StockLowBg else StockAvailableBg,
                modifier = Modifier.fillMaxWidth()
            ) {
                Row(
                    modifier = Modifier.padding(12.dp),
                    horizontalArrangement = Arrangement.SpaceBetween,
                    verticalAlignment = Alignment.CenterVertically
                ) {
                    Text(
                        text = "Suggested Restock Requirement:",
                        fontSize = 12.sp,
                        fontWeight = FontWeight.Medium,
                        color = if (prediction.suggestedRestockQuantity > 0) StockLowAmber else StockAvailableGreen
                    )
                    Text(
                        text = "${prediction.suggestedRestockQuantity} units",
                        fontSize = 14.sp,
                        fontWeight = FontWeight.Bold,
                        color = if (prediction.suggestedRestockQuantity > 0) StockLowAmber else StockAvailableGreen
                    )
                }
            }

            Spacer(modifier = Modifier.height(10.dp))

            Text(
                text = "Reason: ${prediction.riskReason}",
                fontSize = 12.sp,
                color = TextSecondary
            )

            Spacer(modifier = Modifier.height(14.dp))

            Text(
                text = "7-Day Predicted Demand Trajectory",
                fontSize = 13.sp,
                fontWeight = FontWeight.SemiBold,
                color = TextPrimary
            )

            Spacer(modifier = Modifier.height(8.dp))

            // Simple visual bar trajectory for 7 days
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceBetween,
                verticalAlignment = Alignment.Bottom
            ) {
                val maxVal = (prediction.dailyForecasts.maxOfOrNull { it.predictedDemand } ?: 1.0).coerceAtLeast(1.0)

                prediction.dailyForecasts.forEach { forecast ->
                    Column(
                        horizontalAlignment = Alignment.CenterHorizontally,
                        modifier = Modifier.weight(1f)
                    ) {
                        val barHeight = ((forecast.predictedDemand / maxVal) * 60).dp.coerceAtLeast(6.dp)

                        Text(
                            text = "${forecast.predictedDemand.toInt()}",
                            fontSize = 10.sp,
                            fontWeight = FontWeight.Bold,
                            color = PrimaryTeal
                        )

                        Spacer(modifier = Modifier.height(2.dp))

                        Box(
                            modifier = Modifier
                                .width(16.dp)
                                .height(barHeight)
                                .clip(RoundedCornerShape(topStart = 4.dp, topEnd = 4.dp))
                                .background(PrimaryTeal)
                        )

                        Spacer(modifier = Modifier.height(4.dp))

                        Text(
                            text = forecast.dayName.take(3),
                            fontSize = 10.sp,
                            color = TextTertiary
                        )
                    }
                }
            }

            Spacer(modifier = Modifier.height(12.dp))

            Text(
                text = "• ${prediction.disclaimer}",
                fontSize = 10.sp,
                color = TextTertiary,
                lineHeight = 13.sp
            )
        }
    }
}

@Composable
private fun MetricColumn(title: String, value: String) {
    Column(horizontalAlignment = Alignment.CenterHorizontally) {
        Text(text = title, fontSize = 11.sp, color = TextTertiary)
        Spacer(modifier = Modifier.height(2.dp))
        Text(text = value, fontSize = 13.sp, fontWeight = FontWeight.Bold, color = TextPrimary)
    }
}
